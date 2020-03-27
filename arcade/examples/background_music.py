"""
Background Music Example

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_music
"""
import arcade
import time

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300
SCREEN_TITLE = "Starting Template Simple"
MUSIC_VOLUME = 0.5


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.WHITE)

        # Variables used to manage our music. See setup() for giving them
        # values.
        self.music_list = []
        self.current_song = 0
        self.music = None

    def advance_song(self):
        """ Advance our pointer to the next song. This does NOT start the song. """
        self.current_song += 1
        if self.current_song >= len(self.music_list):
            self.current_song = 0
        print(f"Advancing song to {self.current_song}.")

    def play_song(self):
        """ Play the song. """
        # Stop what is currently playing.
        if self.music:
            self.music.stop()

        # Play the next song
        print(f"Playing {self.music_list[self.current_song]}")
        self.music = arcade.Sound(self.music_list[self.current_song], streaming=True)
        self.music.play(MUSIC_VOLUME)
        # This is a quick delay. If we don't do this, our elapsed time is 0.0
        # and on_update will think the music is over and advance us to the next
        # song before starting this one.
        time.sleep(0.03)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # List of music
        self.music_list = [":resources:music/funkyrobot.mp3", ":resources:music/1918.mp3"]
        # Array index of what to play
        self.current_song = 0
        # Play the song
        self.play_song()

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()

        position = self.music.get_stream_position()
        length = self.music.get_length()

        size = 20
        margin = size * .5

        # Print time elapsed and total
        y = SCREEN_HEIGHT - (size + margin)
        text = f"{int(position) // 60}:{int(position) % 60:02} of {int(length) // 60}:{int(length) % 60:02}"
        arcade.draw_text(text, 0, y, arcade.csscolor.BLACK, size)

        # Print current song
        y -= size + margin
        text = f"Currently playing: {self.music_list[self.current_song]}"
        arcade.draw_text(text, 0, y, arcade.csscolor.BLACK, size)

    def on_update(self, dt):

        position = self.music.get_stream_position()

        # The position pointer is reset to 0 right after we finish the song.
        # This makes it very difficult to figure out if we just started playing
        # or if we are doing playing.
        if position == 0.0:
            self.advance_song()
            self.play_song()


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
