import arcade
import pyglet.gl as gl
import ctypes

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

class VertexBuffer:
    def __init__(self, vbo_id: gl.GLuint, size: float):
        self.vbo_id = vbo_id
        self.size = size
        self.color = None


def create_rectangle(center_x: float, center_y: float, width: float,
                     height: float, color):
    """
    This function creates a rectangle using a vertex buffer object.
    Creating the rectangle, and then later drawing it with ``render_rectangle``
    is faster than calling ``draw_rectangle``.
    """
    x1 = -width / 2 + center_x
    y1 = -height / 2 + center_y

    x2 = width / 2 + center_x
    y2 = -height / 2 + center_y

    x3 = width / 2 + center_x
    y3 = height / 2 + center_y

    x4 = -width / 2 + center_x
    y4 = height / 2 + center_y

    data = [x1, y1,
            x2, y2,
            x3, y3,
            x4, y4]

    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(data) // 2)

    shape.color = color
    return shape


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Set up the application.
        """
        super().__init__(width, height, resizable=True)
        self.set_location(20, 20)
        arcade.set_background_color(arcade.color.BLACK)

        self.shape_list = []

        box = create_rectangle(0, 0, 50, 50, arcade.color.RED)
        self.shape_list.append(box)
        box = create_rectangle(60, 60, 5, 5, arcade.color.BLUE)
        self.shape_list.append(box)
        box = create_rectangle(-60, 60, 5, 5, arcade.color.YELLOW)
        self.shape_list.append(box)
        box = create_rectangle(60, -60, 5, 5, arcade.color.GREEN)
        self.shape_list.append(box)
        box = create_rectangle(-60, -60, 5, 5, arcade.color.AFRICAN_VIOLET)
        self.shape_list.append(box)

        self.center_x = 0
        self.center_y = 0


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glLoadIdentity()
        gl.glTranslatef(self.center_x, self.center_y, 0)

        for shape in self.shape_list:

            gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_id)

            gl.glDrawArrays(gl.GL_QUADS, 0, shape.size)
            gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)


    def update(self, delta_time):
        self.center_x += 1
        self.center_y += 1


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
