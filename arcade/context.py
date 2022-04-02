"""
Arcade's version of the OpenGL Context.
Contains pre-loaded programs
"""
from arcade.gl.compute_shader import ComputeShader
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import pyglet
from PIL import Image

import arcade
from arcade.gl import BufferDescription, Context
from arcade.gl.program import Program
from arcade.gl.texture import Texture
from arcade.gl.vertex_array import Geometry
from pyglet.math import Mat4
from arcade.texture_atlas import TextureAtlas


class ArcadeContext(Context):
    """
    An OpenGL context implementation for Arcade with added custom features.
    This context is normally accessed thought :py:attr:`arcade.Window.ctx`.

    Pyglet users can use the base Context class and extend that as they please.

    **This is part of the low level rendering API in arcade
    and is mainly for more advanced usage**

    :param pyglet.window.Window window: The pyglet window
    :param str gc_mode: The garbage collection mode for opengl objects.
                        ``auto`` is just what we would expect in python
                        while ``context_gc`` (default) requires you to call ``Context.gc()``.
                        The latter can be useful when using multiple threads when
                        it's not clear what thread will gc the object.
    """

    atlas_size = 512, 512

    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc"):

        super().__init__(window, gc_mode=gc_mode)

        # Enabled blending by default
        self.enable(self.BLEND)
        self.blend_func = self.BLEND_DEFAULT

        # Set up a default orthogonal projection for sprites and shapes
        self._projection_2d_buffer = self.buffer(reserve=128)
        self._projection_2d_buffer.bind_to_uniform_block(0)
        self.projection_2d = (
            0,
            self.screen.width,
            0,
            self.screen.height,
        )

        # --- Pre-load system shaders here ---
        # FIXME: These pre-created resources needs to be packaged nicely
        #        Just having them globally in the context is probably not a good idea
        self.line_vertex_shader: Program = self.load_program(
            vertex_shader=":resources:shaders/shapes/line/line_vertex_shader_vs.glsl",
            fragment_shader=":resources:shaders/shapes/line/line_vertex_shader_fs.glsl",
        )
        self.line_generic_with_colors_program: Program = self.load_program(
            vertex_shader=":resources:shaders/shapes/line/line_generic_with_colors_vs.glsl",
            fragment_shader=":resources:shaders/shapes/line/line_generic_with_colors_fs.glsl",
        )
        self.shape_element_list_program: Program = self.load_program(
            vertex_shader=":resources:shaders/shape_element_list_vs.glsl",
            fragment_shader=":resources:shaders/shape_element_list_fs.glsl",
        )
        # self.sprite_list_program = self.load_program(
        #     vertex_shader=':resources:shaders/sprites/sprite_list_instanced_vs.glsl',
        #     fragment_shader=':resources:shaders/sprites/sprite_list_instanced_fs.glsl',
        # )
        self.sprite_list_program_no_cull: Program = self.load_program(
            vertex_shader=":resources:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":resources:shaders/sprites/sprite_list_geometry_no_cull_geo.glsl",
            fragment_shader=":resources:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_list_program_no_cull["sprite_texture"] = 0
        self.sprite_list_program_no_cull["uv_texture"] = 1

        self.sprite_list_program_cull: Program = self.load_program(
            vertex_shader=":resources:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":resources:shaders/sprites/sprite_list_geometry_cull_geo.glsl",
            fragment_shader=":resources:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_list_program_cull["sprite_texture"] = 0
        self.sprite_list_program_cull["uv_texture"] = 1

        # Shapes
        self.shape_line_program: Program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/line/unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/line/unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/line/unbuffered_geo.glsl",
        )
        self.shape_ellipse_filled_unbuffered_program: Program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/ellipse/filled_unbuffered_geo.glsl",
        )
        self.shape_ellipse_outline_unbuffered_program: Program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/ellipse/outline_unbuffered_geo.glsl",
        )
        self.shape_rectangle_filled_unbuffered_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/rectangle/filled_unbuffered_geo.glsl",
        )
        self.atlas_resize_program: Program = self.load_program(
            vertex_shader=":resources:/shaders/atlas/resize_vs.glsl",
            geometry_shader=":resources:/shaders/atlas/resize_gs.glsl",
            fragment_shader=":resources:/shaders/atlas/resize_fs.glsl",
        )
        self.atlas_resize_program["atlas_old"] = 0  # Configure texture channels
        self.atlas_resize_program["atlas_new"] = 1
        self.atlas_resize_program["texcoords_old"] = 2
        self.atlas_resize_program["texcoords_new"] = 3
        # SpriteList collision resources
        self.collision_detection_program = self.load_program(
            vertex_shader=":resources:shaders/collision/col_trans_vs.glsl",
            geometry_shader=":resources:shaders/collision/col_trans_gs.glsl",
        )
        self.collision_buffer = self.buffer(reserve=1024 * 4)
        self.collision_query = self.query(samples=False, time=False, primitives=True)

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
        self.shape_ellipse_unbuffered_geometry: Geometry = self.geometry(
            [BufferDescription(self.shape_ellipse_unbuffered_buffer, "2f", ["in_vert"])]
        )
        # ellipse/circle outline
        self.shape_ellipse_outline_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_ellipse_outline_unbuffered_geometry: Geometry = self.geometry(
            [
                BufferDescription(
                    self.shape_ellipse_outline_unbuffered_buffer, "2f", ["in_vert"]
                )
            ]
        )
        # rectangle filled
        self.shape_rectangle_filled_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_rectangle_filled_unbuffered_geometry: Geometry = self.geometry(
            [
                BufferDescription(
                    self.shape_rectangle_filled_unbuffered_buffer, "2f", ["in_vert"]
                )
            ]
        )
        self.atlas_geometry: Geometry = self.geometry()

        self._atlas: Optional[TextureAtlas] = None
        # Global labels we modify in `arcade.draw_text`.
        # These multiple labels with different configurations are stored
        self.pyglet_label_cache: Dict[str, pyglet.text.Label] = {}

        self.active_program = None
        self.point_size = 1.0

    def reset(self) -> None:
        """
        Reset context flags and other states.
        This is mostly used in unit testing.
        """
        self.screen.use(force=True)
        self._projection_2d_buffer.bind_to_uniform_block(0)
        self.active_program = None
        arcade.set_viewport(0, self.window.width, 0, self.window.height)
        self.enable_only(self.BLEND)
        self.blend_func = self.BLEND_DEFAULT
        self.point_size = 1.0

    @property
    def default_atlas(self) -> TextureAtlas:
        """
        The default texture atlas. This is created when arcade is initialized.
        All sprite lists will use use this atlas unless a different atlas
        is passed in the :py:class:`arcade.SpriteList` constructor.

        :type: TextureAtlas
        """
        if not self._atlas:
            # Create the default texture atlas
            # 8192 is a safe maximum size for textures in OpenGL 3.3
            # We might want to query the max limit, but this makes it consistent
            # across all OpenGL implementations.
            self._atlas = TextureAtlas(
                self.atlas_size, border=1, auto_resize=True, ctx=self,
            )

        return self._atlas

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
        self._projection_2d_matrix = Mat4.orthogonal_projection(
            value[0], value[1], value[2], value[3], -100, 100,
        )
        self._projection_2d_buffer.write(self._projection_2d_matrix)

    @property
    def projection_2d_matrix(self) -> Mat4:
        """
        Get the current projection matrix.
        This 4x4 float32 matrix is calculated when setting :py:attr:`~arcade.ArcadeContext.projection_2d`.

        :type: pyglet.math.Mat4
        """
        return self._projection_2d_matrix

    @projection_2d_matrix.setter
    def projection_2d_matrix(self, value: Mat4):
        if not isinstance(value, Mat4):
            raise ValueError("projection_matrix must be a Mat4 object")

        self._projection_2d_matrix = value
        self._projection_2d_buffer.write(self._projection_2d_matrix)

    @contextmanager
    def pyglet_rendering(self):
        """Context manager for pyglet rendering.
        Since arcade and pyglet needs slightly different
        states we needs some initialization and cleanup.

        Examples::

            with window.ctx.pyglet_rendering():
                # Draw with pyglet here
        """
        prev_viewport = self.fbo.viewport
        # Ensure projection and view matrices are set in pyglet
        self.window.projection = self._projection_2d_matrix
        # Global modelview matrix should be set to identity
        self.window.view = Mat4()
        try:
            yield None
        finally:
            # Force arcade.gl to rebind programs
            self.active_program = None
            # Rebind the projection uniform block
            self._projection_2d_buffer.bind_to_uniform_block(binding=0)
            self.enable(self.BLEND, pyglet.gl.GL_SCISSOR_TEST)
            self.blend_func = self.BLEND_DEFAULT
            self.fbo.viewport = prev_viewport

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
        :param Union[str,pathlib.Path] tess_control_shader: Tessellation Control Shader
        :param Union[str,pathlib.Path] tess_evaluation_shader: Tessellation Evaluation Shader
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
            tess_control_src = resolve_resource_path(tess_control_shader).read_text()
            tess_evaluation_src = resolve_resource_path(
                tess_evaluation_shader
            ).read_text()

        return self.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src,
            geometry_shader=geometry_shader_src,
            tess_control_shader=tess_control_src,
            tess_evaluation_shader=tess_evaluation_src,
            defines=defines,
        )

    def load_compute_shader(self, path: Union[str, Path]) -> ComputeShader:
        """
        Loads a compute shader from file. This methods supports
        resource handles.

        Example::

            ctx.load_compute_shader(":shader:compute/do_work.glsl")

        :param Union[str,pathlib.Path] path: Path to texture
        """
        from arcade.resources import resolve_resource_path
        path = resolve_resource_path(path)
        return self.compute_shader(source=path.read_text())

    def load_texture(
        self,
        path: Union[str, Path],
        *,
        flip: bool = True,
        build_mipmaps: bool = False,
    ) -> Texture:
        """
        Loads and creates an OpenGL 2D texture.
        Currently all textures are converted to RGBA for simplicity.

        Example::

            # Load a texture in current working directory
            texture = window.ctx.load_texture("background.png")
            # Load a texture using Arcade resource handle
            texture = window.ctx.load_texture(":textures:background.png")

        :param Union[str,pathlib.Path] path: Path to texture
        :param bool flip: Flips the image upside down
        :param bool build_mipmaps: Build mipmaps for the texture
        """
        from arcade.resources import resolve_resource_path

        path = resolve_resource_path(path)

        image = Image.open(str(path))

        if flip:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        texture = self.texture(
            image.size, components=4, data=image.convert("RGBA").tobytes()
        )
        image.close()

        if build_mipmaps:
            texture.build_mipmaps()

        return texture
