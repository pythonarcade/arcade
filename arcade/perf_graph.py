from typing import List

import arcade
from arcade import Color
import random
import pyglet.clock


class PerfGraph(arcade.Sprite):
    """
    An auto-updating line chart of FPS or event handler execution times.

    It is a subclass of :class:`arcade.Sprite` and can be used with any
    :class:`SpriteList <arcade.SpriteList>` like a regular sprite.

    Unlike other :class:`Sprite <arcade.Sprite>` instances, it neither
    loads an :class:`arcade.Texture` nor accepts one as a constructor
    argument. Instead, it creates a new internal
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
    """
    def __init__(self,
                 width: int, height: int,
                 graph_data: str = "FPS",
                 update_rate: float = 0.1,
                 background_color: Color = arcade.color.BLACK,
                 data_line_color: Color = arcade.color.WHITE,
                 axis_color: Color = arcade.color.DARK_YELLOW,
                 grid_color: Color = arcade.color.DARK_YELLOW,
                 font_color: Color = arcade.color.WHITE,
                 font_size: int = 10):

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
        self.font_color = font_color
        self.font_size = font_size
        pyglet.clock.schedule_interval(self.update_graph, update_rate)

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

        .. warning:: You do not need to call this method!

                     This function will be called automatically!

        :param delta_time: Elapsed time. Passed by the pyglet scheduler
        """
        bottom_y = 15
        left_x = 25

        # Get the sprite list this is part of, return if none
        if self.sprite_lists is None or len(self.sprite_lists) == 0:
            return
        sprite_list = self.sprite_lists[0]

        # Clear and return if timings are disabled
        if not arcade.timings_enabled():
            with sprite_list.atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:
                nothing_color = 0, 0, 0, 0
                fbo.clear(nothing_color)
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

        if len(self.data_to_graph) == 0:
            return

        # Toss old data
        while len(self.data_to_graph) > self.width - left_x:
            self.data_to_graph.pop(0)

        # Set max data
        max_value = max(self.data_to_graph)
        self.max_data = ((max_value + 1.5) // 20 + 1) * 20.0

        # Render to the screen
        with sprite_list.atlas.render_into(self.minimap_texture, projection=self.proj) as fbo:
            fbo.clear(self.background_color)
            max_pixels = self.height - bottom_y
            point_list = []
            x = left_x
            for reading in self.data_to_graph:
                y = (reading / self.max_data) * max_pixels + bottom_y
                point_list.append((x, y))
                x += 1

            # Draw the base line
            arcade.draw_line(left_x, bottom_y, left_x, self.height, self.axis_color)

            # Draw left axis
            arcade.draw_line(left_x, bottom_y, self.width, bottom_y, self.axis_color)

            # Draw number labels
            arcade.draw_text("0", left_x, bottom_y, self.font_color, self.font_size, anchor_x="right", anchor_y="center")  # noqa
            increment = self.max_data // 4
            for i in range(4):
                value = increment * i
                label = f"{int(value)}"
                y = (value / self.max_data) * max_pixels + bottom_y
                arcade.draw_text(label, left_x, y, self.font_color, self.font_size, anchor_x="right",
                                 anchor_y="center")
                arcade.draw_line(left_x, y, self.width, y, self.grid_color)

            # Draw label
            arcade.draw_text(self.graph_data, 0, 2, self.font_color, self.font_size, align="center",
                             width=int(self.width))

            # Draw graph
            arcade.draw_line_strip(point_list, self.line_color)
