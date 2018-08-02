"""
This module provides functionality to manage Sprites.

"""

from typing import Iterable
from typing import TypeVar
from typing import Generic
from typing import List

import pyglet.gl as gl

import math
import numpy as np

from PIL import Image

from arcade.sprite import Sprite
from arcade.sprite import get_distance_between_sprites

from arcade.draw_commands import rotate_point
from arcade.window_commands import get_projection
from arcade import shader

VERTEX_SHADER = """
#version 330
uniform mat4 Projection;
in vec2 in_vert;
in vec2 in_texture;
in vec3 in_pos;
in float in_angle;
in vec2 in_scale;
in vec4 in_sub_tex_coords;
out vec2 v_texture;
void main() {
    mat2 rotate = mat2(
                cos(in_angle), sin(in_angle),
                -sin(in_angle), cos(in_angle)
            );
    vec3 pos;
    pos = in_pos + vec3(rotate * (in_vert * in_scale), 0.);
    gl_Position = Projection * vec4(pos, 1.0);

    vec2 tex_offset = in_sub_tex_coords.xy;
    vec2 tex_size = in_sub_tex_coords.zw;

    v_texture = (in_texture * tex_size + tex_offset) * vec2(1, -1);
}
"""

FRAGMENT_SHADER = """
#version 330
uniform sampler2D Texture;
in vec2 v_texture;
out vec4 f_color;
void main() {
    vec4 basecolor = texture(Texture, v_texture);
    if (basecolor.a == 0.0){
        discard;
    }
    f_color = basecolor;
}
"""


def _create_rects(rect_list: Iterable[Sprite]) -> List[float]:
    """
    Create a vertex buffer for a set of rectangles.
    """

    v2f = []
    for shape in rect_list:
        x1 = -shape.width / 2 + shape.center_x
        x2 = shape.width / 2 + shape.center_x
        y1 = -shape.height / 2 + shape.center_y
        y2 = shape.height / 2 + shape.center_y

        p1 = x1, y1
        p2 = x2, y1
        p3 = x2, y2
        p4 = x1, y2

        if shape.angle:
            p1 = rotate_point(p1[0], p1[1], shape.center_x, shape.center_y, shape.angle)
            p2 = rotate_point(p2[0], p2[1], shape.center_x, shape.center_y, shape.angle)
            p3 = rotate_point(p3[0], p3[1], shape.center_x, shape.center_y, shape.angle)
            p4 = rotate_point(p4[0], p4[1], shape.center_x, shape.center_y, shape.angle)

        v2f.extend([p1[0], p1[1],
                   p2[0], p2[1],
                   p3[0], p3[1],
                   p4[0], p4[1]])

    return v2f


class SpatialHash:
    """
    Structure for fast collision checking.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
    """

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def insert_object_for_box(self, new_object: Sprite):
        """
        Insert a sprite.
        """
        # Get the corners
        min_x = new_object.left
        max_x = new_object.right
        min_y = new_object.bottom
        max_y = new_object.top

        # print(f"New - Center: ({new_object.center_x}, {new_object.center_y}), Angle: {new_object.angle}, "
        #       f"Left: {new_object.left}, Right {new_object.right}")

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Add 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Add 2: {min_point} {max_point}")
        # print("Add: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # append to each intersecting cell
                bucket = self.contents.setdefault((i, j), [])
                if new_object in bucket:
                    # print(f"Error, {new_object.guid} already in ({i}, {j}) bucket. ")
                    pass
                else:
                    bucket.append(new_object)
                    # print(f"Adding {new_object.guid} to ({i}, {j}) bucket. "
                    #       f"{new_object._position} {min_point} {max_point}")

    def remove_object(self, sprite_to_delete: Sprite):
        """
        Remove a Sprite.
        """
        # Get the corners
        min_x = sprite_to_delete.left
        max_x = sprite_to_delete.right
        min_y = sprite_to_delete.bottom
        max_y = sprite_to_delete.top

        # print(f"Del - Center: ({sprite_to_delete.center_x}, {sprite_to_delete.center_y}), "
        #       f"Angle: {sprite_to_delete.angle}, Left: {sprite_to_delete.left}, Right {sprite_to_delete.right}")

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Remove 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Remove 2: {min_point} {max_point}")
        # print("Remove: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), [])
                try:
                    bucket.remove(sprite_to_delete)
                    # print(f"Removing {sprite_to_delete.guid} from ({i}, {j}) bucket. {sprite_to_delete._position} "
                    #       f"{min_point} {max_point}")

                except ValueError:
                    print(f"Warning, tried to remove item {sprite_to_delete.guid} from spatial hash {i} {j} when "
                          f"it wasn't there. {min_point} {max_point}")

    def get_objects_for_box(self, check_object: Sprite) -> List[Sprite]:
        """
        Returns colliding Sprites.
        """
        # Get the corners
        min_x = check_object.left
        max_x = check_object.right
        min_y = check_object.bottom
        max_y = check_object.top

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        close_by_sprites = []
        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # print(f"Checking {i}, {j}")
                # append to each intersecting cell
                new_items = self.contents.setdefault((i, j), [])
                # for item in new_items:
                #     print(f"Found {item.guid} in {i}, {j}")
                close_by_sprites.extend(new_items)

        return close_by_sprites


T = TypeVar('T', bound=Sprite)


class SpriteList(Generic[T]):

    next_texture_id = 0

    def __init__(self, use_spatial_hash=True, spatial_hash_cell_size=128):
        """
        Initialize the sprite list
        """
        # List of sprites in the sprite list
        self.sprite_list = []

        # Used in drawing optimization via OpenGL
        self.program = None
        self.pos_angle_scale = None
        self.pos_angle_scale_buf = None
        self.texture_id = None
        self.texture = None
        self.vao = None
        self.vbo_buf = None

        self.array_of_texture_names = []
        self.array_of_images = []

        # Used in collision detection optimization
        self.spatial_hash = SpatialHash(cell_size=spatial_hash_cell_size)
        self.use_spatial_hash = use_spatial_hash

    def append(self, item: T):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item.register_sprite_list(self)
        self.program = None
        if self.use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def recalculate_spatial_hash(self, item: T):
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.insert_object_for_box(item)

    def remove(self, item: T):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)
        self.program = None
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def update_animation(self):
        """
        Call the update_animation() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update_animation()

    def move(self, change_x: float, change_y: float):
        """
        Moves all contained Sprites.
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def calculate_sprite_buffer(self):

        if len(self.sprite_list) == 0:
            return

        if self.program is None:
            self.program = shader.program(
                vertex_shader=VERTEX_SHADER,
                fragment_shader=FRAGMENT_SHADER
            )

        # Loop through each sprite and grab its position, and the texture it will be using.
        array_of_positions = []
        array_of_sizes = []

        for sprite in self.sprite_list:
            array_of_positions.append([sprite.center_x, sprite.center_y, 0])

            size_h = sprite.height / 2
            size_w = sprite.width / 2
            array_of_sizes.append([size_w, size_h])

        new_array_of_texture_names = []
        new_array_of_images = []
        new_texture = False

        # print()
        # print("New texture start: ", new_texture)
        for sprite in self.sprite_list:
            if sprite.texture_name not in self.array_of_texture_names:
                new_texture = True
                # print("New because of ", sprite.texture_name)

            if sprite.texture_name not in new_array_of_texture_names:
                if sprite.image is not None:
                    new_array_of_texture_names.append(sprite.texture_name)
                    image = sprite.image
                else:
                    new_array_of_texture_names.append(sprite.texture_name)
                    image = Image.open(sprite.texture_name)
                new_array_of_images.append(image)

        # print("New texture end: ", new_texture)
        # print(new_array_of_texture_names)
        # print(self.array_of_texture_names)
        # print()

        if new_texture:
            self.array_of_texture_names = new_array_of_texture_names
            self.array_of_images = new_array_of_images
            # print(f"New Texture Atlas with names {self.array_of_texture_names}")

        # Get their sizes
        widths, heights = zip(*(i.size for i in self.array_of_images))

        # Figure out what size a composite would be
        total_width = sum(widths)
        max_height = max(heights)

        if new_texture:

            if self.texture is not None:
                self.texture.release()

            # Make the composite image
            new_image = Image.new('RGBA', (total_width, max_height))

            x_offset = 0
            for image in self.array_of_images:
                new_image.paste(image, (x_offset, 0))
                x_offset += image.size[0]

            # Create a texture out the composite image
            self.texture = shader.texture(
                (new_image.width, new_image.height),
                4,
                np.asarray(new_image)
            )

            if self.texture_id is None:
                self.texture_id = SpriteList.next_texture_id

                # self.texture = get_opengl_context().texture((new_image.width, new_image.height), 4,
                #                                             np.asarray(new_image))
                # self.texture_id = 100

                # print(f"Using texture id: {self.texture_id}")

            # self.texture_id = SpriteList2.next_texture_id
            # SpriteList2.next_texture_id += 1
            # new_image.save(f"temp_{self.texture_id}.png")
            # print(f"Save temp_{self.texture_id}.png")

        # texture_unit = 0
        # self.texture.use(texture_unit)

        # Create a list with the coordinates of all the unique textures
        tex_coords = []
        start_x = 0.0
        for image in self.array_of_images:
            end_x = start_x + (image.width / total_width)
            normalized_width = image.width / total_width
            start_height = 1 - (image.height / max_height)
            normalized_height = image.height / max_height
            tex_coords.append([start_x, start_height, normalized_width, normalized_height])
            start_x = end_x

        # Go through each sprite and pull from the coordinate list, the proper
        # coordinates for that sprite's image.
        array_of_sub_tex_coords = []
        for sprite in self.sprite_list:
            index = self.array_of_texture_names.index(sprite.texture_name)
            array_of_sub_tex_coords.append(tex_coords[index])

        # Create numpy array with info on location and such
        np_array_positions = np.array(array_of_positions).astype('f4')

        # np_array_angles = (np.random.rand(INSTANCES, 1) * 2 * np.pi).astype('f4')
        np_array_angles = np.tile(np.array(0, dtype=np.float32), (len(self.sprite_list), 1))
        np_array_sizes = np.array(array_of_sizes).astype('f4')
        np_sub_tex_coords = np.array(array_of_sub_tex_coords).astype('f4')
        self.pos_angle_scale = np.hstack((np_array_positions, np_array_angles, np_array_sizes, np_sub_tex_coords))
        self.pos_angle_scale_buf = shader.buffer(self.pos_angle_scale.tobytes())

        vertices = np.array([
            #  x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype=np.float32
        )
        self.vbo_buf = shader.buffer(vertices.tobytes())

        vao_content = [
            (self.vbo_buf, '2f 2f', 'in_vert', 'in_texture'),
            (self.pos_angle_scale_buf, '3f 1f 2f 4f/i', 'in_pos', 'in_angle', 'in_scale', 'in_sub_tex_coords')
        ]

        # Can add buffer to index vertices
        self.vao = shader.vertex_array(self.program, vao_content)

        self.update_positions()

    def update_positions(self):

        if self.program is None:
            return

        for i, sprite in enumerate(self.sprite_list):
            self.pos_angle_scale[i, 0] = sprite.center_x
            self.pos_angle_scale[i, 1] = sprite.center_y
            self.pos_angle_scale[i, 3] = math.radians(sprite.angle)
            self.pos_angle_scale[i, 4] = sprite.width / 2
            self.pos_angle_scale[i, 5] = sprite.height / 2

    def update_position(self, sprite):

        if self.program is None:
            return

        i = self.sprite_list.index(sprite)

        self.pos_angle_scale[i, 0] = sprite.center_x
        self.pos_angle_scale[i, 1] = sprite.center_y
        self.pos_angle_scale[i, 3] = math.radians(sprite.angle)
        self.pos_angle_scale[i, 4] = sprite.width / 2
        self.pos_angle_scale[i, 5] = sprite.height / 2

    def draw(self):

        if len(self.sprite_list) == 0:
            return

        if self.program is None:
            self.calculate_sprite_buffer()

        self.texture.use(0)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        with self.vao:
            self.program['Texture'] = self.texture_id
            self.program['Projection'] = get_projection().flatten()
            self.pos_angle_scale_buf.write(self.pos_angle_scale.tobytes())
            self.vao.render(gl.GL_TRIANGLE_STRIP, instances=len(self.sprite_list))
            self.pos_angle_scale_buf.orphan()

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterable[T]:
        """ Return an iterable object of sprites. """
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def pop(self) -> Sprite:
        """
        Pop off the last sprite in the list.
        """
        self.program = None
        return self.sprite_list.pop()


def get_closest_sprite(sprite1: Sprite, sprite_list: SpriteList) -> (Sprite, float):
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.
    """
    if len(sprite_list) == 0:
        return None

    min_pos = 0
    min_distance = get_distance_between_sprites(sprite1, sprite_list[min_pos])
    for i in range(1, len(sprite_list)):
        distance = get_distance_between_sprites(sprite1, sprite_list[i])
        if distance < min_distance:
            min_pos = i
            min_distance = distance
    return sprite_list[min_pos], min_distance
