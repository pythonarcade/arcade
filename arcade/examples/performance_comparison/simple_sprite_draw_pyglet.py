import pyglet
import timeit

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700


class MyGame(pyglet.window.Window):
    def __init__(self):
        super().__init__(height=SCREEN_HEIGHT, width=SCREEN_WIDTH)

        ball_image = pyglet.image.load('../images/coin_01.png')

        self.batch = pyglet.graphics.Batch()
        self.all_sprites_list = []
        self.draw_time = 0

        # Create the coins
        for x in range(0, SCREEN_WIDTH, 10):
            for y in range(0, SCREEN_HEIGHT, 10):

                # Create the coin instance
                # Coin image from kenney.nl
                coin = pyglet.sprite.Sprite(ball_image, x, y, batch=self.batch)
                self.all_sprites_list.append(coin)


        self.ball = pyglet.sprite.Sprite(ball_image, x=50, y=50)

        pyglet.clock.schedule_interval(self.on_update, 1/60)

    def on_update(self, dtime):
        pass

    def on_draw(self):
        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        self.clear()
        self.batch.draw()

        self.draw_time = timeit.default_timer() - draw_start_time

        sprite_count = len(self.all_sprites_list)
        output = f"Drawing time: {self.draw_time:.4f} for {sprite_count} sprites."
        label = pyglet.text.Label(output, x=20, y=SCREEN_HEIGHT - 20, color=(255,0,0,255), font_size=12, width=2000, align="left", font_name=('Calibri', 'Arial'), anchor_x="left", anchor_y="baseline")
        label.draw()



def main():
    """ Main method """
    window = MyGame()
    pyglet.app.run()

if __name__ == "__main__":
    main()
