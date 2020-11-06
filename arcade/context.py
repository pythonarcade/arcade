"""
Arcade's version of the OpenGL Context.
Contains pre-loaded programs 
"""
from pathlib import Path
from typing import Tuple, Union

from PIL import Image
import pyglet

from arcade.gl import BufferDescription, Context
from arcade.gl.program import Program
from arcade.gl.texture import Texture
import arcade


class ArcadeContext(Context):
    """
    An OpenGL context implementation for Arcade with added custom features.
    This context is normally accessed thought :py:attr:`arcade.Window.ctx`.

    Pyglet users can use the base Context class and extend that as they please.

    **This is part of the low level rendering API in arcade
    and is mainly for more advanced usage**
    """

    def __init__(self, window: pyglet.window.Window):
        """
        :param pyglet.window.Window window: The pyglet window
        """
        super().__init__(window)

        # Set up a default orthogonal projection for sprites and shapes
        self._projection_2d_buffer = self.buffer(reserve=64)
        self._projection_2d_buffer.bind_to_uniform_block(0)
        self._projection_2d_matrix = None
        self.projection_2d = (
            0,
            self.screen.width,
            0,
            self.screen.height,
        )

        # --- Pre-load system shaders here ---
        # FIXME: These pre-created resources needs to be packaged nicely
        #        Just having them globally in the context is probably not a good idea
        self.line_vertex_shader = self.load_program(
            vertex_shader=":resources:shaders/shapes/line/line_vertex_shader_vs.glsl",
            fragment_shader=":resources:shaders/shapes/line/line_vertex_shader_fs.glsl",
        )
        self.line_generic_with_colors_program = self.load_program(
            vertex_shader=":resources:shaders/shapes/line/line_generic_with_colors_vs.glsl",
            fragment_shader=":resources:shaders/shapes/line/line_generic_with_colors_fs.glsl",
        )
        self.shape_element_list_program = self.load_program(
            vertex_shader=":resources:shaders/shape_element_list_vs.glsl",
            fragment_shader=":resources:shaders/shape_element_list_fs.glsl",
        )
        # self.sprite_list_program = self.load_program(
        #     vertex_shader=':resources:shaders/sprites/sprite_list_instanced_vs.glsl',
        #     fragment_shader=':resources:shaders/sprites/sprite_list_instanced_fs.glsl',
        # )
        self.sprite_list_program_no_cull = self.load_program(
            vertex_shader=":resources:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":resources:shaders/sprites/sprite_list_geometry_no_cull_geo.glsl",
            fragment_shader=":resources:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_list_program_cull = self.load_program(
            vertex_shader=":resources:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":resources:shaders/sprites/sprite_list_geometry_cull_geo.glsl",
            fragment_shader=":resources:shaders/sprites/sprite_list_geometry_fs.glsl",
        )

        # Shapes
        self.shape_line_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/line/unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/line/unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/line/unbuffered_geo.glsl",
        )
        self.shape_ellipse_filled_unbuffered_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_geo.glsl",
        )
        self.shape_ellipse_outline_unbuffered_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_geo.glsl",
        )
        self.shape_rectangle_filled_unbuffered_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_geo.glsl",
        )

        # --- Pre-created geometry and buffers for unbuffered draw calls ----
        # FIXME: These pre-created resources needs to be packaged nicely
        #        Just having them globally in the context is probably not a good idea
        self.generic_draw_line_strip_color = self.buffer(reserve=4 * 1000)
        self.generic_draw_line_strip_vbo = self.buffer(reserve=8 * 1000)
        self.generic_draw_line_strip_geometry = self.geometry(
            [
                BufferDescription(self.generic_draw_line_strip_vbo, "2f", ["in_vert"]),
                BufferDescription(
                    self.generic_draw_line_strip_color,
                    "4f1",
                    ["in_color"],
                    normalized=["in_color"],
                ),
            ]
        )
        # Shape line(s)
        # Reserve space for 1000 lines (2f pos, 4f color)
        # TODO: Different version for buffered and unbuffered
        # TODO: Make round-robin buffers
        self.shape_line_buffer_pos = self.buffer(reserve=8 * 10)
        # self.shape_line_buffer_color = self.buffer(reserve=4 * 10)
        self.shape_line_geometry = self.geometry(
            [
                BufferDescription(self.shape_line_buffer_pos, "2f", ["in_vert"]),
                # BufferDescription(self.shape_line_buffer_color, '4f1', ['in_color'], normalized=['in_color'])
            ]
        )
        # ellipse/circle filled
        self.shape_ellipse_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_ellipse_unbuffered_geometry = self.geometry(
            [BufferDescription(self.shape_ellipse_unbuffered_buffer, "2f", ["in_vert"])]
        )
        # ellipse/circle outline
        self.shape_ellipse_outline_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_ellipse_outline_unbuffered_geometry = self.geometry(
            [
                BufferDescription(
                    self.shape_ellipse_outline_unbuffered_buffer, "2f", ["in_vert"]
                )
            ]
        )
        # rectangle filled
        self.shape_rectangle_filled_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_rectangle_filled_unbuffered_geometry = self.geometry(
            [
                BufferDescription(
                    self.shape_rectangle_filled_unbuffered_buffer, "2f", ["in_vert"]
                )
            ]
        )

    @property
    def projection_2d(self) -> Tuple[float, float, float, float]:
        """Get or set the global orthogonal projection for arcade.

        This projection is used by sprites and shapes and is represented
        by four floats: ``(left, right, bottom, top)``

        :type: Tuple[float, float, float, float]
        """
        return self._projection_2d

    @projection_2d.setter
    def projection_2d(self, value: Tuple[float, float, float, float]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError(
                f"projection must be a 4-component tuple, not {type(value)}: {value}"
            )

        self._projection_2d = value
        self._projection_2d_matrix = arcade.create_orthogonal_projection(
            value[0], value[1], value[2], value[3], -100, 100, dtype="f4",
        ).flatten()
        self._projection_2d_buffer.write(self._projection_2d_matrix)

    @property
    def projection_2d_matrix(self):
        """
        Get the current projection matrix as a numpy array.
        This 4x4 float32 matrix is calculated when setting :py:attr:`~arcade.ArcadeContext.projection_2d`.
        """
        return self._projection_2d_matrix

    def load_program(
        self,
        *,
        vertex_shader: Union[str, Path],
        fragment_shader: Union[str, Path] = None,
        geometry_shader: Union[str, Path] = None,
        tess_control_shader: Union[str, Path] = None,
        tess_evaluation_shader: Union[str, Path] = None,
        defines: dict = None,
    ) -> Program:
        """Create a new program given a file names that contain the vertex shader and
        fragment shader. Note that fragment and geometry shader are optional for
        when transform shaders are loaded.

        This method also supports the ``:resources:`` prefix.
        It's recommended to use absolute paths, but not required.

        Example::

            # The most common use case if having a vertex and fragment shader
            program = window.ctx.load_program(
                vertex_shader="vert.glsl",
                fragment_shader="frag.glsl",
            )

        :param Union[str,pathlib.Path] vertex_shader: path to vertex shader
        :param Union[str,pathlib.Path] fragment_shader: path to fragment shader (optional)
        :param Union[str,pathlib.Path] geometry_shader: path to geometry shader (optional)
        :param dict defines: Substitute ``#define`` values in the source
        """
        from arcade.resources import resolve_resource_path

        vertex_shader_src = resolve_resource_path(vertex_shader).read_text()
        fragment_shader_src = None
        geometry_shader_src = None
        tess_control_src = None
        tess_evaluation_src = None

        if fragment_shader:
            fragment_shader_src = resolve_resource_path(fragment_shader).read_text()

        if geometry_shader:
            geometry_shader_src = resolve_resource_path(geometry_shader).read_text()

        if tess_control_shader and tess_evaluation_shader:
            tess_control_src = resolve_resource_path(tess_control_shader)
            tess_evaluation_src = resolve_resource_path(tess_evaluation_shader)

        return self.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src,
            geometry_shader=geometry_shader_src,
            tess_control_shader=tess_control_src,
            tess_evaluation_shader=tess_evaluation_src,
            defines=defines,
        )

    def load_texture(
        self,
        path: Union[str, Path],
        *,
        flip: bool = True,
        build_mipmaps=False,
    ) -> Texture:
        """Loads and creates an OpenGL 2D texture.
        Currently all textures are converted to RGBA.

        Example::

            texture = window.ctx.load_texture("background.png")

        :param Union[str,pathlib.Path] path: Path to texture
        :param bool flip: Flips the image upside down
        :param bool build_mipmaps: Build mipmaps for the texture
        """
        from arcade.resources import resolve_resource_path
        path = resolve_resource_path(path)

        image = Image.open(str(path))

        if flip:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        texture = self.texture(image.size, components=4, data=image.convert("RGBA").tobytes())
        image.close()

        if build_mipmaps:
            texture.build_mipmaps()

        return texture
