import random

import pyglet.clock
from pyglet.graphics import Batch
from pyglet.shapes import Line

import arcade
from arcade.types import RGBA255, Color

__all__ = ["PerfGraph"]


class PerfGraph(arcade.Sprite):
    """
    An auto-updating line chart of FPS or event handler execution times.

    You must use :func:`arcade.enable_timings` to turn on performance
    tracking for the chart to display data.

    Aside from instantiation and updating the chart, this class behaves
    like other :class:`arcade.Sprite` instances. You can use it with
    :class:`SpriteList <arcade.SpriteList>` normally. See
    :ref:`performance_statistics_example` for an example of how to use
    this class.

    Unlike other :class:`Sprite <arcade.Sprite>` instances, this class
    neither loads an :class:`arcade.Texture` nor accepts one as a
    constructor argument. Instead, it creates a new internal
    :class:`Texture <arcade.Texture>` instance. The chart is
    automatically redrawn to this internal
    :class:`Texture <arcade.Texture>` every ``update_rate`` seconds.

    Args:
        width (int):
            The width of the chart texture in pixels
        height (int):
            The height of the chart texture in pixels
        graph_data (str):
            The pyglet event handler or statistic to track
        update_rate (float):
            How often the graph updates, in seconds
        background_color (RGBA255):
            The background color of the chart
        data_line_color (RGBA255):
            Color of the line tracking drawn
        axis_color (RGBA255):
            The color to draw the x & y axes in
        font_color (RGBA255):
            The color of the label font
        font_size (int):
            The size of the label font in points
        y_axis_num_lines (int):
            How many grid lines should be used to divide the y scale of the graph.
        view_y_scale_step (float):
            The graph's view area will be scaled to a multiple of this value to
            fit to the data currently displayed.
    """

    def __init__(
        self,
        width: int,
        height: int,
        graph_data: str = "FPS",
        update_rate: float = 0.1,
        background_color: RGBA255 = arcade.color.BLACK,
        data_line_color: RGBA255 = arcade.color.WHITE,
        axis_color: RGBA255 = arcade.color.DARK_YELLOW,
        grid_color: RGBA255 = arcade.color.DARK_YELLOW,
        font_color: RGBA255 = arcade.color.WHITE,
        font_size: int = 10,
        y_axis_num_lines: int = 4,
        view_y_scale_step: float = 20.0,
    ):
        unique_id = str(random.random())
        self.minimap_texture = arcade.Texture.create_empty(unique_id, (width, height))
        super().__init__(self.minimap_texture)
        self.proj = 0, self.width, 0, self.height

        # The data line is redrawn each update by a function that does
        # not cache vertices, so there is no need to make this attribute
        # a property that updates geometry when set.
        self.line_color = Color.from_iterable(data_line_color)
        """The color of the line tracking the data."""

        # Store visual style info for cached pyglet shape geometry
        self._background_color = Color.from_iterable(background_color)
        self._grid_color = Color.from_iterable(grid_color)
        self._axis_color = Color.from_iterable(axis_color)
        self._font_color = Color.from_iterable(font_color)
        self._font_size = font_size
        self._y_axis_num_lines = y_axis_num_lines
        self._left_x = 25
        self._bottom_y = 15

        # Variables for rendering the data line
        self.graph_data = graph_data
        """The graphed data type, either "FPS" or a pyglet event handler name."""

        self._data_to_graph: list[float] = []
        self._view_max_value = 0.0  # We'll calculate this once we have data
        self._view_y_scale_step = view_y_scale_step
        self._view_height = self._texture.height - self._bottom_y  # type: ignore
        self._y_increment = self._view_height / self._y_axis_num_lines

        # Set up internal Text object & line caches

        self._pyglet_batch = Batch()  # Used to draw graph elements

        # Convenient storage for iteration during color updates
        self._vertical_axis_text_objects: list[arcade.Text] = []
        self._all_text_objects: list[arcade.Text] = []
        self._grid_lines: list[Line] = []

        # Create the bottom label text object
        self._bottom_label = arcade.Text(
            graph_data,
            0,
            2,
            self._font_color,
            self._font_size,
            align="center",
            width=int(width),
        )
        self._all_text_objects.append(self._bottom_label)

        # Create the axes
        self._x_axis = Line(
            self._left_x,
            self._bottom_y,
            self._left_x,
            height,
            batch=self._pyglet_batch,
            color=self._axis_color,
        )

        self._y_axis = Line(
            self._left_x,
            self._bottom_y,
            width,
            self._bottom_y,
            batch=self._pyglet_batch,
            color=self._axis_color,
        )

        # Create the Y scale text objects & lines
        for i in range(self._y_axis_num_lines):
            y_level = self._bottom_y + self._y_increment * i
            self._vertical_axis_text_objects.append(
                arcade.Text(
                    "0",  # Ensure the lowest y axis label is always 0
                    self._left_x,
                    int(y_level),
                    self._font_color,
                    self._font_size,
                    anchor_x="right",
                    anchor_y="center",
                )
            )
            self._grid_lines.append(
                Line(
                    self._left_x,
                    y_level,
                    width,
                    y_level,
                    batch=self._pyglet_batch,
                    color=self._grid_color,
                )
            )

        self._all_text_objects.extend(self._vertical_axis_text_objects)

        # Enable auto-update
        pyglet.clock.schedule_interval(self.update_graph, update_rate)

    @property
    def background_color(self) -> Color:
        """Get or set the background color of the graph."""
        return self._background_color

    @background_color.setter
    def background_color(self, new_color: RGBA255):
        self._background_color = Color.from_iterable(new_color)

    @property
    def grid_color(self) -> Color:
        """Get or set the color of the grid lines."""
        return self._grid_color

    @grid_color.setter
    def grid_color(self, raw_color: RGBA255):
        new_color = Color.from_iterable(raw_color)
        for grid_line in self._grid_lines:
            grid_line.color = new_color

    @property
    def axis_color(self) -> Color:
        """Get or set the color of the x and y axes."""
        return self._axis_color

    @axis_color.setter
    def axis_color(self, raw_color: RGBA255):
        new_color = Color.from_iterable(raw_color)
        self._x_axis.color = new_color
        self._y_axis.color = new_color

    @property
    def font_size(self) -> int:
        """Get or set the font size of the labels."""
        return self._font_size

    @font_size.setter
    def font_size(self, new: int):
        self._font_size = new
        for text in self._all_text_objects:
            text.font_size = new

    @property
    def font_color(self) -> Color:
        """Get or set the font color of the labels."""
        return self._font_color

    @font_color.setter
    def font_color(self, raw_color: Color):
        new_color = Color.from_iterable(raw_color)
        self._font_color = new_color
        for text in self._all_text_objects:
            text.color = new_color

    def remove_from_sprite_lists(self) -> None:
        """
        Remove the sprite from all lists and cancel the update event.
        """
        super().remove_from_sprite_lists()

        # It is very important to call this to prevent potential
        # issues such as crashes or excess memory use from failed
        # garbage collection.
        pyglet.clock.unschedule(self.update)

    def update_graph(self, delta_time: float) -> None:
        """
        Update the graph by redrawing the internal texture data.

        .. warning:: You do not need to call this method! It will be
                     called automatically!

        Args:
            delta_time: Elapsed time in seconds. Passed by the pyglet
                        scheduler.
        """

        # Skip update if there is no SpriteList that can draw this graph
        if self.sprite_lists is None or len(self.sprite_lists) == 0:
            return

        sprite_list = self.sprite_lists[0]
        atlas = sprite_list.atlas

        # Clear and return if timings are disabled
        if not arcade.timings_enabled():
            # Please forgive the ugly spacing. It makes type checking work.
            with atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:  # type: ignore
                fbo.clear(color=(0, 0, 0, 255))
            return

        # Get FPS and add to our historical data
        data_to_graph = self._data_to_graph
        graph_data = self.graph_data
        if graph_data == "FPS":
            data_to_graph.append(arcade.get_fps())
        else:
            timings = arcade.get_timings()
            if graph_data in timings:
                timing_list = timings[self.graph_data]
                avg_timing = sum(timing_list) / len(timing_list)
                data_to_graph.append(avg_timing * 1000)

        # Skip update if there is no data to graph
        if len(data_to_graph) == 0:
            return

        # Using locals for frequently used values is faster than
        # looking up instance variables repeatedly.
        bottom_y = self._bottom_y
        left_x = self._left_x
        view_y_scale_step = self._view_y_scale_step
        vertical_axis_text_objects = self._vertical_axis_text_objects
        view_height = self._view_height

        # We have to render at the internal texture's original size to
        # prevent distortion and bugs when the sprite is scaled.
        texture_width, texture_height = self._texture.size  # type: ignore

        # Toss old data by removing leftmost entries
        while len(data_to_graph) > texture_width - left_x:
            data_to_graph.pop(0)

        # Calculate the value at the top of the chart
        max_value = max(data_to_graph)
        view_max_value = ((max_value + 1.5) // view_y_scale_step + 1) * view_y_scale_step

        # Calculate draw positions of each pixel on the data line
        point_list = []
        x = left_x
        for reading in data_to_graph:
            y = (reading / view_max_value) * view_height + bottom_y
            point_list.append((x, y))
            x += 1

        # Update the view scale & labels if needed
        if view_max_value != self._view_max_value:
            self._view_max_value = view_max_value
            view_y_legend_increment = self._view_max_value // self._y_axis_num_lines
            for index in range(1, len(vertical_axis_text_objects)):
                text_object = vertical_axis_text_objects[index]
                text_object.text = f"{int(index * view_y_legend_increment)}"

        # Render to the internal texture
        # This ugly spacing is intentional to make type checking work.
        with atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:  # type: ignore
            # Set the background color
            fbo.clear(color=self.background_color)

            # Draw lines & their labels
            for text in self._all_text_objects:
                text.draw()
            self._pyglet_batch.draw()

            # Draw the data line
            arcade.draw_line_strip(point_list, self.line_color)
