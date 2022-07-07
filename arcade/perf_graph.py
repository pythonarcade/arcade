from typing import List

import arcade
from arcade import Color
import random
import pyglet.clock


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

    :param width: The width of the chart texture in pixels
    :param height: The height of the chart texture in pixels
    :param graph_data: The pyglet event handler or statistic to track
    :param update_rate: How often the graph updates, in seconds
    :param background_color: The background color of the chart
    :param data_line_color: Color of the line tracking drawn
    :param axis_color: The color to draw the x & y axes in
    :param font_color: The color of the label font
    :param font_size: The size of the label font in points
    :param y_axis_data_step: The amount the maximum Y value of the graph
                             view will shrink or grow by to fit to the
                             data currently displayed.
    """
    def __init__(
            self,
            width: int, height: int,
            graph_data: str = "FPS",
            update_rate: float = 0.1,
            background_color: Color = arcade.color.BLACK,
            data_line_color: Color = arcade.color.WHITE,
            axis_color: Color = arcade.color.DARK_YELLOW,
            grid_color: Color = arcade.color.DARK_YELLOW,
            font_color: Color = arcade.color.WHITE,
            font_size: int = 10,
            y_axis_data_step: float = 20.0,
    ):

        unique_id = str(random.random())

        self.minimap_texture = arcade.Texture.create_empty(unique_id, (width, height))
        super().__init__(texture=self.minimap_texture)
        self.background_color = background_color
        self.line_color = data_line_color
        self.grid_color = grid_color
        self.data_to_graph: List[float] = []
        self.proj = 0, self.width, 0, self.height
        self.axis_color = axis_color
        self.graph_data = graph_data
        self.max_data = 0.0
        self._font_color = font_color
        self._font_size = font_size
        self.y_axis_data_step = y_axis_data_step
        self.left_x = 25
        self.bottom_y = 15
        self.max_pixels = self.height - self.bottom_y
        self._num_subdivisions = 4

        value_increment = self.max_data // self._num_subdivisions
        y_increment = self.max_pixels / self._num_subdivisions

        # set up internal Text object caches
        self.vertical_axis_text_objects = []
        self.all_text_objects = []

        # Create the bottom label text object
        self.bottom_label = arcade.Text(
            graph_data, 0, 2, self._font_color, self._font_size, align="center", width=int(width))
        self.all_text_objects.append(self.bottom_label)

        # Create the Y axis text objects
        for i in range(self._num_subdivisions):
            self.vertical_axis_text_objects.append(
                arcade.Text(
                    f"{int(value_increment * i)}",
                    self.left_x, self.bottom_y + y_increment * i,
                    self._font_color, self._font_size,
                    anchor_x="right", anchor_y="center"))
        self.all_text_objects.extend(self.vertical_axis_text_objects)

        # Enable auto-update
        pyglet.clock.schedule_interval(self.update_graph, update_rate)

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, new: int):
        self._font_size = new
        for text in self.all_text_objects:
            text.font_size = new

    @property
    def font_color(self) -> Color:
        return self._font_color

    @font_color.setter
    def font_color(self, new: Color):
        self._font_color = new
        for text in self.all_text_objects:
            text.color = new

    def remove_from_sprite_lists(self):
        """
        Remove the sprite from all lists and cancel the update event.

        :return:
        """
        super().remove_from_sprite_lists()

        # It is very important to call this to prevent potential
        # issues such as crashes or excess memory use from failed
        # garbage collection.
        pyglet.clock.unschedule(self.update)

    def update_graph(self, delta_time: float):
        """
        Update the graph by redrawing the internal texture data.

        .. warning:: You do not need to call this method! It will be
                     called automatically!

        :param delta_time: Elapsed time. Passed by the pyglet scheduler
        """

        # Using locals for frequently used values is faster than
        # looking up instance variables repeatedly.
        bottom_y = self.bottom_y
        left_x = self.left_x
        y_axis_data_step = self.y_axis_data_step
        vertical_axis_text_objects = self.vertical_axis_text_objects

        # Get the sprite list this is part of, return if none
        if self.sprite_lists is None or len(self.sprite_lists) == 0:
            return
        sprite_list = self.sprite_lists[0]

        # Clear and return if timings are disabled
        if not arcade.timings_enabled():
            with sprite_list.atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:
                fbo.clear()
            return

        # Get FPS and add to our historical data
        if self.graph_data == "FPS":
            self.data_to_graph.append(arcade.get_fps())
        else:
            timings = arcade.get_timings()
            if self.graph_data in timings:
                timing_list = timings[self.graph_data]
                avg_timing = sum(timing_list) / len(timing_list)
                self.data_to_graph.append(avg_timing * 1000)

        # Skip update if there is no data to graph
        if len(self.data_to_graph) == 0:
            return

        # Toss old data
        while len(self.data_to_graph) > self.width - left_x:
            self.data_to_graph.pop(0)

        # Calculate the value at the top of the chart
        max_value = max(self.data_to_graph)
        max_data = ((max_value + 1.5) // y_axis_data_step + 1) * y_axis_data_step

        # Calculate draw positions of pixels on the chart
        max_pixels = self.height - bottom_y
        point_list = []
        x = left_x
        for reading in self.data_to_graph:
            y = (reading / max_data) * max_pixels + bottom_y
            point_list.append((x, y))
            x += 1

        # Update the Y axis scale & labels if needed
        if max_data != self.max_data:
            self.max_data = max_data
            value_increment = self.max_data // 4
            for index in range(1, len(vertical_axis_text_objects)):
                text_object = vertical_axis_text_objects[index]
                text_object.text = f"{int(index * value_increment)}"

        # Render to the screen
        with sprite_list.atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:
            fbo.clear(self.background_color)

            # Draw the base line
            arcade.draw_line(left_x, bottom_y, left_x, self.height, self.axis_color)

            # Draw left axis
            arcade.draw_line(left_x, bottom_y, self.width, bottom_y, self.axis_color)

            # Draw lines & their labels
            for text in vertical_axis_text_objects:
                grid_line_y = text.y
                arcade.draw_line(
                    left_x, grid_line_y,
                    self.width, grid_line_y,
                    self.grid_color)
                text.draw()
            self.bottom_label.draw()

            # Draw graph
            arcade.draw_line_strip(point_list, self.line_color)
