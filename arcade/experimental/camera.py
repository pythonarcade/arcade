
import arcade
import pyglet

class Camera2D:
    def __init__(self, width, height):
        
        # Window dimensions
        self.width = width
        self.height = height

        self.width_center = width // 2
        self.height_center = height // 2

        # Amount the camera moves, in world space
        self.x = 0
        self.y = 0

        # Get the monitor display width and height for centering the app window
        screen = pyglet.canvas.Display().get_default_screen()

        self.screen_width = screen.width
        self.screen_height = screen.height
        
        # The zoomed dimensions
        self.zoom_width = width
        self.zoom_height = height

        self.zoom_left = 0
        self.zoom_right = width
        self.zoom_bottom = 0
        self.zoom_top = height

        # Margin
        self.margin_left = 0
        self.margin_right = 0
        self.margin_bottom = 0
        self.margin_top = 0

        self.scroll_curr_step = 0.2

        self.old_x = 0
        self.old_y = 0

    def reset_viewport(self):
        """ Resets the viewport to default (Used for static objects like GUI) """

        arcade.set_viewport(0, self.width, 0, self.height)

    def set_viewport(self):
        """ Updates the viewport with the new position and zoom """

        self.left = self.zoom_left + self.x - self.width_center
        self.right = self.zoom_right + self.x - self.width_center
        self.bottom = self.zoom_bottom + self.y - self.height_center
        self.top = self.zoom_top + self.y - self.height_center
        
        arcade.set_viewport(self.left, self.right, self.bottom, self.top)

    def scroll_to(self, x, y):
        """ Scrolls the camera to position """
        
        diff_x = x - self.x
        diff_y = y - self.y

        # Simple smooth scrolling with margin
        if diff_x < self.margin_left:
            self.x += (diff_x - self.margin_left) * self.scroll_curr_step
        elif diff_x > self.margin_right:
            self.x += (diff_x - self.margin_right) * self.scroll_curr_step
        if diff_y < self.margin_bottom:
            self.y += (diff_y - self.margin_bottom) * self.scroll_curr_step
        elif diff_y > self.margin_top:
            self.y += (diff_y - self.margin_top) * self.scroll_curr_step

        self.old_x = x
        self.old_y = y

    def set_margin(self, left, right, top, bottom):
        """ Sets the margin """
        self.margin_left = -left
        self.margin_right = right
        self.margin_bottom = -bottom
        self.margin_top = top

    def zoom(self, amount: float):
        """ Zooms in/out by a multiple """
        # This could probably be set to a single variable, just beware of zero div errors
        self.zoom_width *= amount
        self.zoom_height *= amount

        # Prevents the camera from inverting
        if self.zoom_width < self.width * 0.54:
            self.zoom_width = self.width * 0.54 + 0.1
        if self.zoom_height < self.height * 0.54:
            self.zoom_height = self.height * 0.54 + 0.1

        self.update_zoom()

    def update_zoom(self):
        """ Update zoomed variables """
        self.zoom_left   = self.width - self.zoom_width
        self.zoom_right  = self.zoom_width
        self.zoom_bottom = self.height - self.zoom_height
        self.zoom_top    = self.zoom_height

    def resize(self, width, height):
        """ Called when window is resized """

        scale_x = width / self.width
        scale_y = height / self.height

        self.zoom_width *= scale_x
        self.zoom_height *= scale_y

        self.width = width
        self.height = height

        self.width_center = width // 2
        self.height_center = height // 2

        self.update_zoom()
        self.set_viewport()
        
    def mouse_to_world_coordinates(self, x, y):
        """ Returns the position of the mouse in world space. """
        return (x / self.width * (self.right - self.left) + self.left,
            y / self.height * (self.top - self.bottom) + self.bottom)
