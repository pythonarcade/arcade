from .draw_commands import *
from .geometry import *


class SpriteList():
    """
    List of sprites.

    :Unit Test:

    >>> import arcade
    >>> import random
    >>> arcade.open_window("Sprite Example", 600, 600)
    >>> scale = 1
    >>> meteor_list = arcade.SpriteList()
    >>> filename = "doc/source/examples/images/meteorGrey_big1.png"
    >>> for i in range(100):
    ...     meteor = arcade.Sprite(filename, scale)
    ...     meteor.center_x = random.random() * 2 - 1
    ...     meteor.center_y = random.random() * 2 - 1
    ...     meteor_list.append(meteor)
    >>> meteor_list.remove(meteor) # Remove last meteor, just to test
    >>> m = meteor_list.pop() # Remove another meteor, just to test
    >>> meteor_list.update() # Call update on all items
    >>> print(len(meteor_list))
    98
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> meteor_list.draw()
    >>> arcade.finish_render()
    >>> for meteor in meteor_list:
    ...     meteor.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self):
        self.sprite_list = []

    def append(self, item):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item._register_sprite_list(self)

    def remove(self, item):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def draw(self):
        """
        Call the draw() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.draw()

    def __len__(self):
        return len(self.sprite_list)

    def __iter__(self):
        return iter(self.sprite_list)

    def pop(self):
        """
        Pop off the last sprite in the list.
        """
        return self.sprite_list.pop()


class Sprite():
    """
    Class that represents a 'sprite' on-screen.

    @attribute someArg: example argument

    Attributes:
        :scale:           blah blah x.
        :center_x:        blah blah x.
        :center_y:        blah blah x.
        :angle:           blah blah x.
        :change_x:        blah blah x.
        :change_y:        blah blah x.
        :change_angle:    blah blah x.
        :alpha:           blah blah x.
        :sprite_lists:     blah blah x.
        :textures:         blah blah x.
        :cur_texture_index: blah blah x.
        :transparent:      blah blah x.

    :Example:

    >>> import arcade
    >>> arcade.open_window("Sprite Example", 800, 600)
    >>> SCALE = 1
    >>> # Test creating an empty sprite
    >>> empty_sprite = arcade.Sprite()
    >>> # Create a sprite with an image
    >>> filename = "doc/source/examples/images/playerShip1_orange.png"
    >>> ship_sprite = arcade.Sprite(filename, SCALE)
    >>> # Draw the sprite
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> ship_sprite.draw()
    >>> arcade.finish_render()
    >>> # Move the sprite
    >>> ship_sprite.change_x = 1
    >>> ship_sprite.change_y = 1
    >>> ship_sprite.update() # Move/update the ship
    >>> # Remove the sprite
    >>> ship_sprite.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self, filename=None, scale=1, x=0, y=0, width=0, height=0):
        """
        Create a new sprite.

        Args:
            filename (str): Filename of an image that represents the sprite.
            scale (float): Scale the image up or down. Scale of 1.0 is no-scaling.
            x (float): Scale the image up or down. Scale of 1.0 is no-scaling.
            y (float): Scale the image up or down. Scale of 1.0 is no-scaling.
            width (float): Width of the sprite
            height (float): Height of the sprite

        """

        if width < 0:
            raise SystemError("Width of image can't be less than zero.")

        if height < 0:
            raise SystemError("Height of image can't be less than zero.")

        if width == 0 and height != 0:
            raise SystemError("Width can't be zero.")

        if height == 0 and width != 0:
            raise SystemError("Height can't be zero.")

        if filename is not None:
            self.texture = load_texture(filename, x, y,
                                        width, height)

            self.textures = [self.texture]
            self.width = self.texture.width * scale
            self.height = self.texture.height * scale
        else:
            self.textures = []
            self.width = 0
            self.height = 0

        self.cur_texture_index = 0
        self.scale = scale
        self.center_x = 0
        self.center_y = 0
        self.angle = 0.0

        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

        self.alpha = 1.0
        self.sprite_lists = []
        self.transparent = True

    def append_texture(self, texture):
        self.textures.append(texture)

    def set_texture(self, texture_no):
        self.texture = self.textures[texture_no]
        self.cur_texture_index = texture_no
        self.width = self.textures[texture_no].width * self.scale
        self.height = self.textures[texture_no].height * self.scale

    def get_texture(self):
        return self.cur_texture_index

    def set_position(self, center_x, center_y):
        """
        Set a sprite's position
        """
        self.center_x = center_x
        self.center_y = center_y

    def get_points(self):
        """
        Get the corner points for the rect that makes up the sprite.
        """
        x1, y1 = rotate(self.center_x - self.width / 2,
                        self.center_y - self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x2, y2 = rotate(self.center_x + self.width / 2,
                        self.center_y - self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x3, y3 = rotate(self.center_x + self.width / 2,
                        self.center_y + self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x4, y4 = rotate(self.center_x - self.width / 2,
                        self.center_y + self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)

        return ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

    points = property(get_points)

    def _get_bottom(self):
        """
        Return the y coordinate of the bottom of the sprite.

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0
        >>> print(ship_sprite.bottom)
        -37.5
        >>> ship_sprite.bottom = 1
        >>> print(ship_sprite.bottom)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        return min(points[0][1], points[1][1], points[2][1], points[3][1])

    def _set_bottom(self, amount):
        """
        Set the location of the sprite based on the bottom y coordinate.
        """
        points = self.get_points()
        lowest = min(points[0][1], points[1][1], points[2][1], points[3][1])
        diff = lowest - amount
        self.center_y -= diff

    bottom = property(_get_bottom, _set_bottom)

    def _get_top(self):
        """
        Return the y coordinate of the top of the sprite.

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0
        >>> print(ship_sprite.top)
        37.5
        >>> ship_sprite.top = 1
        >>> print(ship_sprite.top)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        return max(points[0][1], points[1][1], points[2][1], points[3][1])

    def _set_top(self, amount):
        """ The highest y coordinate. """
        points = self.get_points()
        highest = max(points[0][1], points[1][1], points[2][1], points[3][1])
        diff = highest - amount
        self.center_y -= diff

    top = property(_get_top, _set_top)

    def _get_left(self):
        """
        Left-most coordinate.

        :Example:

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0
        >>> print(ship_sprite.left)
        -49.5
        >>> ship_sprite.left = 1
        >>> print(ship_sprite.left)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        return min(points[0][0], points[1][0], points[2][0], points[3][0])

    def _set_left(self, amount):
        """ The left most x coordinate. """
        points = self.get_points()
        leftmost = min(points[0][0], points[1][0], points[2][0], points[3][0])
        diff = amount - leftmost
        self.center_x += diff

    left = property(_get_left, _set_left)

    def _get_right(self):
        """
        Return the x coordinate of the right-side of the sprite.

        :Example:

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0
        >>> print(ship_sprite.right)
        49.5
        >>> ship_sprite.right = 1
        >>> print(ship_sprite.right)
        1.0
        >>> arcade.quick_run(0.25)
        """

        points = self.get_points()
        return max(points[0][0], points[1][0], points[2][0], points[3][0])

    def _set_right(self, amount):
        """ The right most x coordinate. """
        points = self.get_points()
        rightmost = max(points[0][0], points[1][0], points[2][0], points[3][0])
        diff = rightmost - amount
        self.center_x -= diff

    right = property(_get_right, _set_right)

    def _get_texture(self):
        """
        Return the texture that the sprite uses.
        """
        return self._texture

    def _set_texture(self, texture):
        """
        Set the current sprite texture.
        """
        if type(texture) is Texture:
            self._texture = texture
            self.width = texture.width
            self.height = texture.height
        else:
            raise SystemError("Can't set the texture to something that is " +
                              "not an instance of the Texture class.")

    texture = property(_get_texture, _set_texture)

    def _register_sprite_list(self, new_list):
        """
        Register this sprite as belonging to a list. We will automatically
        remove ourselves from the the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

    def draw(self):
        """
        Draw the sprite.
        """
        draw_texture_rect(self.center_x, self.center_y,
                          self.width, self.height,
                          self.texture, self.angle, self.alpha,
                          self.transparent)

    def update(self):
        """
        Update the sprite.
        """
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.angle += self.change_angle

    def kill(self):
        """
        Remove the sprite from all sprite lists.
        """
        for sprite_list in self.sprite_lists:
            if self in sprite_list:
                sprite_list.remove(self)


class AnimatedSprite(Sprite):
    """
    Sprite for platformer games that supports animations.

    >>> import arcade
    >>> arcade.open_window("Sprite Example", 800, 600)
    >>> player = arcade.AnimatedSprite()
    >>> top_trim = 100
    >>> ltrim = 2
    >>> rtrim = 2
    >>> image_location_list = [
    ... [520 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 0 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1548 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1290 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim]]
    >>> filename = "doc/source/examples/images/spritesheet_complete.png"
    >>> texture_info_list = arcade.load_textures(filename, image_location_list)
    >>> for texture_info in texture_info_list:
    ...     texture = texture_info
    ...     player.append_texture(texture)
    >>> texture_info_list = arcade.load_textures(\
filename, image_location_list, True)
    >>> for texture_info in texture_info_list:
    ...     texture = texture_info
    ...     player.append_texture(texture)
    >>> player.set_left_walk_textures([12, 13])
    >>> player.set_right_walk_textures([5, 6])
    >>> player.set_left_jump_textures([10])
    >>> player.set_right_jump_textures([3])
    >>> player.set_left_stand_textures([11])
    >>> player.set_right_stand_textures([4])
    >>> player.texture_change_distance = 5
    >>> player.speed = 10
    >>> player.set_position(5, 5)
    >>> player.jump()
    >>> player.change_x = 10 # Jump
    >>> player.change_y = 1
    >>> player.update()
    >>> player.go_left()
    >>> player.update()
    >>> player.update()
    >>> player.update()
    >>> player.stop_left()
    >>> player.update()
    >>> player.face_left()
    >>> player.update()
    >>> player.change_x = -10 #Left
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.go_left()
    >>> player.update()
    >>> player.stop_left()
    >>> player.update()
    >>> player.face_right()
    >>> player.change_x = 10 # Right
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.go_right()
    >>> player.update()
    >>> player.update()
    >>> player.stop_right()
    >>> player.update()
    >>> player.stop_right()
    >>> player.change_x = 0 # Stop
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self):
        super().__init__()
        self.last_change_x = self.center_x
        self.facing = "right"
        self.left_walk_textures = []
        self.right_walk_textures = []
        self.up_walk_textures = []
        self.down_walk_textures = []
        self.jump_textures = []
        self.left_stand_textures = []
        self.right_stand_textures = []
        self.up_stand_textures = []
        self.down_stand_textures = []
        self.jump_speed = 10
        self.cur_texture_index = 0
        self.texture_change_distance = 0
        self.speed = 5

    def update(self):
        """
        Logic for selecting the proper texture to use.
        """
        super().update()
        # print("Update change_x={} change_y={}".format(self.change_x, self.change_y))
        if self.change_y == 0.0:
            if self.change_x < 0:
                if abs(self.last_change_x - self.center_x) > \
                        self.texture_change_distance:
                    if self.cur_texture_index in self.left_textures:
                        pos = self.left_textures.index(self.cur_texture_index)\
                            + 1
                    else:
                        pos = 0
                    if pos >= len(self.left_textures):
                        pos = 0
                    self.set_texture(self.left_textures[pos])
                    self.last_change_x = self.center_x

            elif self.change_x > 0:
                if abs(self.last_change_x - self.center_x) \
                        > self.texture_change_distance:
                    if self.cur_texture_index in self.right_textures:
                        i = self.cur_texture_index
                        pos = self.right_textures.index(i) + 1
                    else:
                        pos = 0
                    if pos >= len(self.right_textures):
                        pos = 0
                    self.set_texture(self.right_textures[pos])
                    self.last_change_x = self.center_x
            else:
                if self.facing == "right":
                    self.set_texture(self.right_stand_textures[0])
                if self.facing == "left":
                    self.set_texture(self.left_stand_textures[0])

        else:
            if self.facing == "right":
                self.set_texture(self.jump_right_textures[0])
            if self.facing == "left":
                self.set_texture(self.jump_left_textures[0])

    def set_left_walk_textures(self, texture_index_list):
        self.left_textures = texture_index_list

    def set_right_walk_textures(self, texture_index_list):
        self.right_textures = texture_index_list

    def set_left_jump_textures(self, texture_index_list):
        self.jump_left_textures = texture_index_list

    def set_right_jump_textures(self, texture_index_list):
        self.jump_right_textures = texture_index_list

    def set_left_stand_textures(self, texture_index_list):
        self.left_stand_textures = texture_index_list

    def set_right_stand_textures(self, texture_index_list):
        self.right_stand_textures = texture_index_list

    def go_left(self):
        self.change_x = -self.speed

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0

    def go_right(self):
        self.change_x = self.speed

    def stop_right(self):
        if self.change_x > 0:
            self.change_x = 0

    def face_left(self):
        if self.facing != "left":
            self.facing = "left"

    def face_right(self):
        if self.facing != "right":
            self.facing = "right"

    def jump(self):
        self.change_y = self.jump_speed
