"""
A 2D camera.

Features:
* Scrolling
* Zooming
* Aspect ratio locking
* Scroll limits
* Scaling
* linear/nearest zoom/scrolling
"""
from typing import Tuple
import arcade


class Camera2D:

    def __init__(self, *, viewport: Tuple[int, int, int, int], projection: Tuple[float, float, float, float],
                 ):
        """Test"""
        self._window = arcade.get_window()
        self._viewport = viewport
        self._projection = projection
        self._scroll_x: float = 0
        self._scroll_y: float = 0
        self._zoom: float = 0

    def mouse_coordinates_to_world(self, x, y) -> Tuple[float, float]:
        """
        Converts mouse coordinates to world coordinates.
        This returns the actual x and y position the mouse pointer
        is located in your game world regardless of scrolling
        or zoom level.

        :rtype: Tuple[float, float]
        """
        # Account for black borders in viewport
        vp = self._adjust_viewport_to_aspect_ratio(self.aspect_ratio, self._viewport)
        # Account for projection (including zoom)
        vp_width, vp_height = vp[2], vp[3]
        proj_width, proj_height = self._projection[1] - self._projection[0], self._projection[3] - self._projection[2]
        dx, dy = proj_width / vp_width, proj_height / vp_height

        return (
            (x - vp[0]) * dx + self._scroll_x,
            (y - vp[1]) * dy + self._scroll_y,
        )

    # Mouse coordinates to screen (relative)

    def _adjust_viewport_to_aspect_ratio(self, aspect_ratio: float, viewport: Tuple[int, int, int, int]):
        """
        Calculate viewport base on aspect ratio
        adding black borders when needed
        """
        width, height = self._viewport[2], self._viewport[3]

        expected_width = int(height * aspect_ratio)
        expected_height = int(expected_width / aspect_ratio)

        if expected_width > width:
            expected_width = width
            expected_height = int(expected_width / aspect_ratio)

        blank_space_x = width - expected_width
        blank_space_y = height - expected_height
        return (
            blank_space_x // 2 + self._viewport[0], 
            blank_space_y // 2 + self._viewport[1],
            expected_width,
            expected_height,
        )

    @property
    def aspect_ratio(self) -> float:
        """
        Get the aspect ratio of the projection

        :type: float
        """
        return (self._projection[1] - self._projection[0]) / (self._projection[3] - self._projection[2])

    @property
    def window(self):
        """The window this camera belongs to"""
        return self._window

    @property
    def projection(self) -> Tuple[float, float, float, float]:
        """
        Get or set the orthographic projection::

            # Project 0 -> 800 (x) and 0 -> 600 on the viewport
            camera.projection = 0, 800, 0, 600

        :type: Tuple[float, float, float, float]
        """
        return self._projection

    @projection.setter
    def projection(self, value):
        self._projection = value

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        Get or set the viewport::

            # Define what part of the screen should be rendered to
            camera.viewport = 0, 0, 800, 600

        :type: Tuple[int, int, int, int]
        """
        return self._viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]):
        if not isinstance(value, tuple) and len(value) == 4:
            raise ValueError("viewport must be a 4-component tuple")

        self._viewport = value

    @property
    def scroll(self) -> Tuple[float, float]:
        """
        Get or set the x and y scroll

        :type: Tuple[float, float]
        """
        return self._scroll_x, self._scroll_y

    @scroll.setter
    def scroll(self, value: Tuple[float, float]):
        self._scroll_x, self.scroll_y = value

    @property
    def scroll_x(self) -> float:
        """
        Get or set the scroll value on the x axis

        :type: float
        """
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: float):
        self._scroll = value

    @property
    def scroll_y(self) -> float:
        """
        Get or set the scroll value on the y axis

        :type: float
        """
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: float):
        self._scroll_y = value

    @property
    def zoom(self) -> float:
        """
        Get or set the zoom value

        :type: float
        """
        return self._zoom

    @zoom.setter
    def zoom(self, value: float):
        self._zoom = value

    def use(self):
        """Make the camera active"""
        # Calculate aspect ratio from projection
        ar = self.aspect_ratio

        # Apply scrolling
        proj = (
            self._projection[0] + self._scroll_x,
            self._projection[1] + self._scroll_x,
            self._projection[2] + self._scroll_y,
            self._projection[3] + self._scroll_y,
        )

        # Ensure aspect ratio is maintained
        vp = self._adjust_viewport_to_aspect_ratio(ar, self._viewport)

        # Apply pixel ratio scaling
        scale = arcade.get_scaling_factor(self._window)
        vp_scaled = tuple(int(v * scale) for v in vp)

        self._window.ctx.viewport = vp_scaled
        self._window.ctx.projection_2d = proj


# class Camera2D:
#     def __init__(self, width, height):

#         # Window dimensions
#         self.width = width
#         self.height = height

#         self.width_center = width // 2
#         self.height_center = height // 2

#         # Amount the camera moves, in world space
#         self.x = 0
#         self.y = 0

#         # Get the monitor display width and height for centering the app window
#         screen = pyglet.canvas.Display().get_default_screen()

#         self.screen_width = screen.width
#         self.screen_height = screen.height

#         # The zoomed dimensions
#         self.zoom_width = width
#         self.zoom_height = height

#         self.zoom_left = 0
#         self.zoom_right = width
#         self.zoom_bottom = 0
#         self.zoom_top = height

#         # Margin
#         self.margin_left = 0
#         self.margin_right = 0
#         self.margin_bottom = 0
#         self.margin_top = 0

#         self.scroll_curr_step = 0.2

#         self.old_x = 0
#         self.old_y = 0

#     def reset_viewport(self):
#         """ Resets the viewport to default (Used for static objects like GUI) """

#         arcade.set_viewport(0, self.width, 0, self.height)

#     def set_viewport(self):
#         """ Updates the viewport with the new position and zoom """

#         self.left = self.zoom_left + self.x - self.width_center
#         self.right = self.zoom_right + self.x - self.width_center
#         self.bottom = self.zoom_bottom + self.y - self.height_center
#         self.top = self.zoom_top + self.y - self.height_center

#         arcade.set_viewport(self.left, self.right, self.bottom, self.top)

#     def scroll_to(self, x, y):
#         """ Scrolls the camera to position """

#         diff_x = x - self.x
#         diff_y = y - self.y

#         # Simple smooth scrolling with margin
#         if diff_x < self.margin_left:
#             self.x += (diff_x - self.margin_left) * self.scroll_curr_step
#         elif diff_x > self.margin_right:
#             self.x += (diff_x - self.margin_right) * self.scroll_curr_step
#         if diff_y < self.margin_bottom:
#             self.y += (diff_y - self.margin_bottom) * self.scroll_curr_step
#         elif diff_y > self.margin_top:
#             self.y += (diff_y - self.margin_top) * self.scroll_curr_step

#         self.old_x = x
#         self.old_y = y

#     def set_margin(self, left, right, top, bottom):
#         """ Sets the margin """
#         self.margin_left = -left
#         self.margin_right = right
#         self.margin_bottom = -bottom
#         self.margin_top = top

#     def zoom(self, amount: float):
#         """ Zooms in/out by a multiple """
#         # This could probably be set to a single variable, just beware of zero div errors
#         self.zoom_width *= amount
#         self.zoom_height *= amount

#         # Prevents the camera from inverting
#         if self.zoom_width < self.width * 0.54:
#             self.zoom_width = self.width * 0.54 + 0.1
#         if self.zoom_height < self.height * 0.54:
#             self.zoom_height = self.height * 0.54 + 0.1

#         self.update_zoom()

#     def update_zoom(self):
#         """ Update zoomed variables """
#         self.zoom_left   = self.width - self.zoom_width
#         self.zoom_right  = self.zoom_width
#         self.zoom_bottom = self.height - self.zoom_height
#         self.zoom_top    = self.zoom_height

#     def resize(self, width, height):
#         """ Called when window is resized """

#         scale_x = width / self.width
#         scale_y = height / self.height

#         self.zoom_width *= scale_x
#         self.zoom_height *= scale_y

#         self.width = width
#         self.height = height

#         self.width_center = width // 2
#         self.height_center = height // 2

#         self.update_zoom()
#         self.set_viewport()

#     def mouse_to_world_coordinates(self, x, y):
#         """ Returns the position of the mouse in world space. """
#         return (x / self.width * (self.right - self.left) + self.left,
#             y / self.height * (self.top - self.bottom) + self.bottom)
