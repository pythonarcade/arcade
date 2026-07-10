"""A game main menu with animated widgets.

This example combines two new GUI features:

- :class:`UIAnimatedGroup` renders a widget subtree into a cached surface,
  which can be drawn with rotation, scaling, fading and tinting.
  The wrapped widgets are only re-rendered when they actually change,
  animating the group itself is basically free.
- Animations (:meth:`UIAnimatedGroup.animate`) tween properties over time and
  support sequencing (``then()``), repetition (``repeat``, ``yoyo``) and
  relative targets (``rel()``). Starting a new animation takes over its
  properties from running ones, so state changes like hover just start
  a new animation.

The menu shows:

- the whole menu popping in when the view is shown, and fading out on "Quit"
- a gently pulsing and swaying title
- buttons popping in staggered, popping and wiggling when hovered
- decorative spinning letter tiles
- a spinning "Play" button when clicked

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_animations
"""

from __future__ import annotations

from typing import Callable

import arcade
import pyglet
from arcade import uicolor
from arcade.anim import Easing
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIFlatButton,
    UILabel,
    UIView,
    UIWidget,
    bind,
)
from arcade.gui.experimental import Animation, UIAnimatedGroup, rel
from arcade.types import Color

BACKGROUND = Color(110, 148, 132)
TILE_COLORS = [
    uicolor.GREEN_GREEN_SEA,
    uicolor.RED_ALIZARIN,
    uicolor.YELLOW_SUN_FLOWER,
    uicolor.DARK_BLUE_WET_ASPHALT,
]

IdleFactory = Callable[["AnimatedWidget"], Animation]
"""Starts an idle animation on a group and returns it, so it can be stopped."""


def pulse(scale=1.05, period=1.2) -> IdleFactory:
    """Idle animation: gently pulsing scale."""

    def start(group: AnimatedWidget) -> Animation:
        return group.animate(
            scale=scale, duration=period / 2, ease=Easing.SINE, repeat=True, yoyo=True
        )

    return start


def sway(angle=2.0, period=2.4) -> IdleFactory:
    """Idle animation: swaying 0 -> angle -> -angle -> 0, forever."""

    def start(group: AnimatedWidget) -> Animation:
        return (
            group.animate(angle=angle, duration=period / 4, ease=Easing.SINE, repeat=True)
            .then(angle=-angle, duration=period / 2, ease=Easing.SINE)
            .then(angle=0.0, duration=period / 4, ease=Easing.SINE)
        )

    return start


def spin(period=8.0) -> IdleFactory:
    """Idle animation: endless clockwise rotation."""

    def start(group: AnimatedWidget) -> Animation:
        return group.animate(angle=rel(-360), duration=period, repeat=True)

    return start


class AnimatedWidget(UIAnimatedGroup):
    """A UIAnimatedGroup with little animation helpers.

    Args:
        child: The wrapped widget.
        idle: Optional idle animation factory (or list of factories),
            started after entrance and hover animations finish.
    """

    def __init__(
        self,
        *,
        child: UIWidget,
        idle: IdleFactory | list[IdleFactory] | None = None,
    ):
        super().__init__(child=child)
        self._idle_factories = [idle] if callable(idle) else list(idle or [])
        self._idle_animations: list[Animation] = []

    def start_idle(self):
        """(Re-)start the idle animations, unless the group is hovered."""
        if self.hovered:
            return
        self.stop_idle()
        self._idle_animations = [factory(self) for factory in self._idle_factories]

    def stop_idle(self):
        for animation in self._idle_animations:
            animation.stop()
        self._idle_animations = []

    def pop_in(self, delay: float = 0.0):
        """Scale and fade in, then continue with the idle animation."""
        self.scale = 0.0
        self.alpha = 0
        self.animate(scale=1.0, duration=0.5, delay=delay, ease=Easing.BACK_OUT).on_finish(
            self.start_idle
        )
        self.animate(alpha=255, duration=0.35, delay=delay)

    def pop_on_hover(self, scale: float = 1.08, angle: float = 2.5):
        """Pop and wiggle while the group is hovered."""

        def on_hover_change():
            if self.hovered:
                self.stop_idle()
                self.animate(scale=scale, duration=0.15, ease=Easing.BACK_OUT)
                self.animate(angle=angle, duration=0.06).then(angle=-angle, duration=0.12).then(
                    angle=0.0, duration=0.06
                )
                # in case an interrupted entrance left the group transparent
                self.animate(alpha=255, duration=0.1)
            else:
                self.animate(scale=1.0, angle=0.0, duration=0.15).on_finish(self.start_idle)

        bind(self, "hovered", on_hover_change)


class MainMenuView(UIView):
    def __init__(self):
        super().__init__()
        # self.ui._pixelated = True

        self.background_color = BACKGROUND

        root = UIAnchorLayout(size_hint=(1, 1))

        # title, gently pulsing and swaying
        title = UILabel(
            "New GUI\nAnimations",
            font_size=72,
            bold=True,
            multiline=True,
            align="center",
            text_color=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
        )
        self.title = AnimatedWidget(child=title, idle=[pulse(1.04, 2.4), sway(2, 2.4)])
        root.add(self.title, anchor_x="center", anchor_y="top", align_y=-60)

        # main menu buttons, the resume button pulses to attract attention
        resume = AnimatedWidget(
            child=UIFlatButton(text="Resume", width=240, height=50),
            idle=pulse(1.05, 1.2),
        )
        play = AnimatedWidget(child=UIFlatButton(text="Play", width=240, height=50))
        quit_ = AnimatedWidget(
            child=UIFlatButton(text="Quit", width=240, height=50, style=UIFlatButton.STYLE_RED)
        )
        self.menu_buttons = [resume, play, quit_]

        menu = UIBoxLayout(space_between=12)
        for group in self.menu_buttons:
            group.pop_on_hover()
            menu.add(group)
        root.add(menu, anchor_x="center", anchor_y="center", align_y=-40)

        # side menu buttons
        self.side_buttons = []
        side = UIBoxLayout(space_between=8)
        for text in ("Leaderboard", "Librarium", "Settings", "Credits"):
            group = AnimatedWidget(child=UIFlatButton(text=text, width=180, height=36))
            group.pop_on_hover(scale=1.1)
            self.side_buttons.append(group)
            side.add(group)
        root.add(side, anchor_x="left", anchor_y="bottom", align_x=40, align_y=40)

        # decorative letter tiles, slowly spinning or swaying
        self.tiles = []
        for letter, color, anchor, align, idle in [
            ("N", TILE_COLORS[0], ("left", "top"), (140, -90), spin(9)),
            ("E", TILE_COLORS[1], ("left", "center"), (230, 30), sway(14, 4)),
            ("V", TILE_COLORS[2], ("right", "top"), (-380, -10), sway(-10, 5)),
            ("B", TILE_COLORS[3], ("right", "bottom"), (-200, 20), spin(12)),
        ]:
            label = UILabel(letter, font_size=26, bold=True, text_color=uicolor.WHITE_CLOUDS)
            tile = (
                label.with_padding(all=12)
                .with_background(color=color)
                .with_border(width=3, color=uicolor.DARK_BLUE_MIDNIGHT_BLUE)
            )
            group = AnimatedWidget(child=tile, idle=idle)
            self.tiles.append(group)
            root.add(
                group, anchor_x=anchor[0], anchor_y=anchor[1], align_x=align[0], align_y=align[1]
            )

        # the whole menu is wrapped in another group, to fade it out on quit
        self.root_group = AnimatedWidget(child=root)
        self.add_widget(self.root_group)

        play.child.on_click = self.on_play
        quit_.child.on_click = self.on_quit
        self._play_group = play

    def on_show_view(self):
        super().on_show_view()

        # staggered entrance animation
        self.title.pop_in(delay=0.1)
        for i, group in enumerate(self.menu_buttons):
            group.pop_in(delay=0.3 + i * 0.1)
        for i, group in enumerate(self.side_buttons):
            group.pop_in(delay=0.6 + i * 0.08)
        for i, group in enumerate(self.tiles):
            group.pop_in(delay=0.9 + i * 0.1)

    def on_play(self, event):
        """Spin the play button once."""
        self._play_group.animate(angle=rel(-360), duration=0.6, ease=Easing.CUBIC)

    def on_quit(self, event):
        """Scale and fade out the whole menu, then close the window."""
        group = self.root_group
        group.animate(alpha=0, duration=0.5, ease=Easing.SINE_IN)
        group.animate(scale=0.8, duration=0.5, ease=Easing.SINE_IN).then(duration=0.1).on_finish(
            arcade.exit
        )


def main():
    window = arcade.Window(1280, 720, "GUI Example: Animated Main Menu", resizable=True)
    window.show_view(MainMenuView())
    arcade.run()


if __name__ == "__main__":
    pyglet.options.text_antialiasing = False

    main()
