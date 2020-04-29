
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

        self.camera_lag = 2

        self.scroll_step = 0.005
        self.scroll_min_step = 0.1
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

        diff_x = self.x - x
        diff_y = self.y - y

        # 
        # if diff_x > self.camera_lag \
        #     or diff_y > self.camera_lag \
        #     or (x == self.old_x and y == self.old_y and self.scroll_curr_step < 1
        # ):
        #     self.scroll_curr_step += self.scroll_step
        # else:
        #     self.scroll_curr_step = self.scroll_min_step

        # Simple smooth scrolling
        if abs(diff_x) > self.camera_lag:
            self.x = self.x - self.scroll_curr_step * diff_x
            # self.x = Maths.lerp(self.x, x, 0.95)
            # self.x = self.x - Maths.smoothstep(0, 1, self.scroll_curr_step) * diff_x
        if abs(diff_y) > self.camera_lag:
            self.y = self.y - self.scroll_curr_step * diff_y
            # self.y = Maths.lerp(self.y, y, 0.95)
            # self.y = self.y - Maths.smoothstep(0, 1, self.scroll_curr_step) * diff_y

        self.old_x = x
        self.old_y = y

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
