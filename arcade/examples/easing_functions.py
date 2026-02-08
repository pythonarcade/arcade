"""
Example showing the different easing functions.

If Python and Arcade are installed, this example can be
run from the command line with:
python -m arcade.examples.easing_functions
"""

import arcade
from arcade import SpriteCircle, SpriteList
from arcade.anim.easing import Easing, ease
from arcade.clock import GLOBAL_CLOCK
from arcade.types.rect import LBWH, Rect

from pyglet.graphics import Batch  # type: ignore -- Batch isn't in __all__?

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Easing Example"

# Load our brand font
arcade.resources.load_josefin_sans()

# Load an actually good monospace font
arcade.load_font(":system:fonts/ttf/Fira Code/Fira_Code_Medium.ttf")

# Label all the functions
# There's nine "types", not counting linear, and three of each.

EASING_TYPES = 10
EASING_SUB_TYPES = 3

easing_functions = {
    "Linear": Easing.LINEAR,
    "Sine": Easing.SINE,
    "Sine In": Easing.SINE_IN,
    "Sine Out": Easing.SINE_OUT,
    "Quad": Easing.QUAD,
    "Quad In": Easing.QUAD_IN,
    "Quad Out": Easing.QUAD_OUT,
    "Cubic": Easing.CUBIC,
    "Cubic In": Easing.CUBIC_IN,
    "Cubic Out": Easing.CUBIC_OUT,
    "Quart": Easing.QUART,
    "Quart In": Easing.QUART_IN,
    "Quart Out": Easing.QUART_OUT,
    "Quint": Easing.QUINT,
    "Quint In": Easing.QUINT_IN,
    "Quint Out": Easing.QUINT_OUT,
    "Expo": Easing.EXPO,
    "Expo In": Easing.EXPO_IN,
    "Expo Out": Easing.EXPO_OUT,
    "Circ": Easing.CIRC,
    "Circ In": Easing.CIRC_IN,
    "Circ Out": Easing.CIRC_OUT,
    "Back": Easing.BACK,
    "Back In": Easing.BACK_IN,
    "Back Out": Easing.BACK_OUT,
    "Elastic": Easing.ELASTIC,
    "Elastic In": Easing.ELASTIC_IN,
    "Elastic Out": Easing.ELASTIC_OUT,
    "Bounce": Easing.BOUNCE,
    "Bounce In": Easing.BOUNCE_IN,
    "Bounce Out": Easing.BOUNCE_OUT,
}

# We need these for sorting them later;
# they're in reverse order since we draw bottom-up.
function_names = [
    "Bounce",
    "Elastic",
    "Back",
    "Circ",
    "Expo",
    "Quint",
    "Quart",
    "Cubic",
    "Quad",
    "Sine",
    "Linear",
]


def px_to_pt(px: int) -> int:
    return round(px // (4 / 3))

LINE_WIDTH = 2

class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.ARCADE_GREEN
        self.time = 0.0
        self.paused = False

        # "Layouting"
        rect = self.window.rect
        self.areas: list[Rect] = []
        # We want a 10 x 3 grid, but pretending there's an 12 x 3 grid
        # and we're ignoring the first two rows.
        buffer = 10  # px
        cols = EASING_SUB_TYPES
        rows = EASING_TYPES + 2
        rect_width = rect.width / cols
        rect_height = rect.height / rows

        # Generate a gird of rectangles. We'll use these to place the
        # easing demos.
        for i in range(EASING_TYPES * EASING_SUB_TYPES + 1):
            new_rect = LBWH(0, 0, rect_width, rect_height)
            row = i // cols
            col = i % cols
            if col == 0:
                new_rect = new_rect.align_left(rect.left)
            elif col == 1:
                new_rect = new_rect.align_center_x(rect.center_x)
            elif col == 2:
                new_rect = new_rect.align_right(rect.right)
            new_rect = new_rect.align_bottom(rect.bottom + rect_height * row)
            new_rect = new_rect.resize(new_rect.width - buffer,
                                       new_rect.height - buffer)
            self.areas.append(new_rect)

        self.random_colors = [arcade.types.Color.random(a=255)
                              for _ in range(len(self.areas))]

        self.title_text = arcade.Text(
            "Easing Functions",
            buffer,
            self.window.rect.top - buffer,
            font_size=px_to_pt(int(rect_height - buffer)),
            font_name="Josefin Sans",
            anchor_y="top",
        )
        self.subtitle_text = arcade.Text(
            "Press [SPACE] to pause/unpause.",
            self.window.rect.right - buffer,
            self.window.rect.top - buffer,
            font_size=px_to_pt(int(rect_height - buffer) // 2),
            font_name="Josefin Sans",
            color=arcade.color.ARCADE_YELLOW,
            anchor_y="top",
            anchor_x="right",
        )

        self.labels = []
        self.progress_labels = []
        self.text_batch = Batch()
        self.sprites = []
        self.spritelist = SpriteList()
        for n, a in enumerate(self.areas):
            name = self.idx_to_func_name(n)
            func = easing_functions[name]
            label = arcade.Text(
                func.__name__,
                a.left,
                a.bottom,
                font_size=px_to_pt(int(a.height / 2 - buffer)),
                font_name="Fira Code",
                batch=self.text_batch,
            )
            self.labels.append(label)
            progress_label = arcade.Text(
                "0.00",
                a.right,
                a.bottom,
                font_size=px_to_pt(int(a.height / 2 - buffer)),
                font_name="Josefin Sans",
                bold="light",
                anchor_x="right",
                batch=self.text_batch,
            )
            self.progress_labels.append(progress_label)
            sprite = SpriteCircle(int(a.height / 4), arcade.color.ARCADE_YELLOW)
            sprite.left = a.left
            sprite.center_y = a.bottom + (a.height * 0.75)
            self.sprites.append(sprite)
            self.spritelist.append(sprite)

        self.lines = []
        for a in self.areas:
            y = a.bottom + (a.height * 0.75)
            # Long line
            self.lines.extend([(a.left + LINE_WIDTH, y), (a.right - LINE_WIDTH, y)])
            # Left line
            self.lines.extend([(a.left + LINE_WIDTH, y - buffer),
                               (a.left + LINE_WIDTH, y + buffer)])
            # Center line
            self.lines.extend([(a.center_x, y - buffer), (a.center_x, y + buffer)])
            # Right line
            self.lines.extend([(a.right - LINE_WIDTH, y - buffer),
                               (a.right - LINE_WIDTH, y + buffer)])

    def idx_to_func_name(self, i: int) -> str:
        if i >= len(self.areas):
            raise ValueError
        else:
            t = function_names[i // 3]
            if i % 3 == 0:
                return t
            elif i % 3 == 1:
                return f"{t} In"
            else:
                return f"{t} Out"

    def on_update(self, delta_time):
        if int(GLOBAL_CLOCK.time) % 4 == 0:
            self.time = 1 - (GLOBAL_CLOCK.time % 1)
        elif int(GLOBAL_CLOCK.time) % 4 == 1:
            self.time = 0
        elif int(GLOBAL_CLOCK.time) % 4 == 2:
            self.time = GLOBAL_CLOCK.time % 1
        else:
            self.time = 1

        for n, a in enumerate(self.areas):
            name = self.idx_to_func_name(n)
            func = easing_functions[name]
            sprite = self.sprites[n]

            right = a.right - sprite.width
            x = ease(a.left, right, 0, 1, self.time, func)
            p = ease(0.0, 1.0, 0, 1, self.time, func)
            rounded_p = round(p, 2)
            sprite.left = x
            self.progress_labels[n].text = f"{rounded_p:.02}"
            if rounded_p > 1 or rounded_p < 0:
                self.progress_labels[n].color = arcade.color.PINK_PEARL
            else:
                self.progress_labels[n].color = arcade.color.WHITE

    def on_draw(self):
        """
        Render the screen.
        """
        self.clear()
        self.title_text.draw()
        self.subtitle_text.draw()
        for n, r in enumerate(self.areas):
            arcade.draw_rect_filled(r, arcade.color.BLACK.replace(a=64))
        arcade.draw_lines(self.lines, arcade.color.WHITE, LINE_WIDTH)
        self.text_batch.draw()
        self.spritelist.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle key press events"""
        if symbol == arcade.key.ESCAPE:
            self.window.close()
        if symbol == arcade.key.SPACE:
            self.paused = not self.paused
            if self.paused:
                GLOBAL_CLOCK.set_tick_speed(0)
            else:
                GLOBAL_CLOCK.set_tick_speed(1)


def main():
    """Main function."""
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
