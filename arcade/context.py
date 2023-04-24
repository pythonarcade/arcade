"""
Arcade's version of the OpenGL Context.
Contains pre-loaded programs
"""
from pathlib import Path
from typing import Any, Iterable, Dict, Optional, Tuple, Union, Sequence
from contextlib import contextmanager

import pyglet
from pyglet import gl
from pyglet.graphics.shader import UniformBufferObject
from PIL import Image

import arcade
from arcade.gl import BufferDescription, Context
from arcade.gl.compute_shader import ComputeShader
from arcade.gl.program import Program
from arcade.gl.texture import Texture2D
from arcade.gl.vertex_array import Geometry
from arcade.gl.framebuffer import Framebuffer
from pyglet.math import Mat4
from arcade.texture_atlas import TextureAtlas

__all__ = ["ArcadeContext"]

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

    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc", gl_api: str = "gl"):

        super().__init__(window, gc_mode=gc_mode, gl_api=gl_api)

        # Enabled blending by default
        self.enable(self.BLEND)
        self.blend_func = self.BLEND_DEFAULT

        # Set up a default orthogonal projection for sprites and shapes
        self._window_block: UniformBufferObject = window.ubo
        self.bind_window_block()
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
            vertex_shader=":system:shaders/shapes/line/line_vertex_shader_vs.glsl",
            fragment_shader=":system:shaders/shapes/line/line_vertex_shader_fs.glsl",
        )
        self.line_generic_with_colors_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/line/line_generic_with_colors_vs.glsl",
            fragment_shader=":system:shaders/shapes/line/line_generic_with_colors_fs.glsl",
        )
        self.shape_element_list_program: Program = self.load_program(
            vertex_shader=":system:shaders/shape_element_list_vs.glsl",
            fragment_shader=":system:shaders/shape_element_list_fs.glsl",
        )
        self.sprite_list_program_no_cull: Program = self.load_program(
            vertex_shader=":system:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":system:shaders/sprites/sprite_list_geometry_no_cull_geo.glsl",
            fragment_shader=":system:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_list_program_no_cull["sprite_texture"] = 0
        self.sprite_list_program_no_cull["uv_texture"] = 1

        self.sprite_list_program_cull: Program = self.load_program(
            vertex_shader=":system:shaders/sprites/sprite_list_geometry_vs.glsl",
            geometry_shader=":system:shaders/sprites/sprite_list_geometry_cull_geo.glsl",
            fragment_shader=":system:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_list_program_cull["sprite_texture"] = 0
        self.sprite_list_program_cull["uv_texture"] = 1

        # Shapes
        self.shape_line_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/line/unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/line/unbuffered_fs.glsl",
            geometry_shader=":system:shaders/shapes/line/unbuffered_geo.glsl",
        )
        self.shape_ellipse_filled_unbuffered_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/ellipse/filled_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/ellipse/filled_unbuffered_fs.glsl",
            geometry_shader=":system:shaders/shapes/ellipse/filled_unbuffered_geo.glsl",
        )
        self.shape_ellipse_outline_unbuffered_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/ellipse/outline_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/ellipse/outline_unbuffered_fs.glsl",
            geometry_shader=":system:shaders/shapes/ellipse/outline_unbuffered_geo.glsl",
        )
        self.shape_rectangle_filled_unbuffered_program = self.load_program(
            vertex_shader=":system:shaders/shapes/rectangle/filled_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/rectangle/filled_unbuffered_fs.glsl",
            geometry_shader=":system:shaders/shapes/rectangle/filled_unbuffered_geo.glsl",
        )
        # Atlas shaders
        self.atlas_resize_program: Program = self.load_program(
            vertex_shader=":system:shaders/atlas/resize_vs.glsl",
            geometry_shader=":system:shaders/atlas/resize_gs.glsl",
            fragment_shader=":system:shaders/atlas/resize_fs.glsl",
        )
        self.atlas_resize_program["atlas_old"] = 0  # Configure texture channels
        self.atlas_resize_program["atlas_new"] = 1
        self.atlas_resize_program["texcoords_old"] = 2
        self.atlas_resize_program["texcoords_new"] = 3

        # SpriteList collision resources
        self.collision_detection_program = self.load_program(
            vertex_shader=":system:shaders/collision/col_trans_vs.glsl",
            geometry_shader=":system:shaders/collision/col_trans_gs.glsl",
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
        self.label_cache: Dict[str, arcade.Text] = {}

        # self.active_program = None
        self.point_size = 1.0

    def reset(self) -> None:
        """
        Reset context flags and other states.
        This is mostly used in unit testing.
        """
        self.screen.use(force=True)
        self.bind_window_block()
        # self.active_program = None
        arcade.set_viewport(0, self.window.width, 0, self.window.height)
        self.enable_only(self.BLEND)
        self.blend_func = self.BLEND_DEFAULT
        self.point_size = 1.0

    def bind_window_block(self) -> None:
        """
        Binds the projection and view uniform buffer object.
        This should always be bound to index 0 so all shaders
        have access to them.
        """
        gl.glBindBufferRange(
            gl.GL_UNIFORM_BUFFER,
            0,
            self._window_block.buffer.id,
            0,
            128,  # 32 x 32bit floats (two mat4)
        )

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
                self.atlas_size, border=2, auto_resize=True, ctx=self,
            )

        return self._atlas

    @property
    def projection_2d(self) -> Tuple[float, float, float, float]:
        """Get or set the global orthogonal projection for arcade.

        This projection is used by sprites and shapes and is represented
        by four floats: ``(left, right, bottom, top)``

        When reading this property we reconstruct the projection parameters
        from pyglet's projection matrix. When setting this property
        we construct an orthogonal projection matrix and set it in pyglet.

        :type: Tuple[float, float, float, float]
        """
        mat = self.window.projection

        # Reconstruct the projection values from the matrix
        # TODO: Take scale into account
        width = 2.0 / mat[0]
        height = 2.0 / mat[5]
        a = width * mat[12]
        b = height * mat[13]
        left = -(width + a) / 2
        right = left + width
        bottom = -(height + b) / 2
        top = bottom + height

        return left, right, bottom, top

    @projection_2d.setter
    def projection_2d(self, value: Tuple[float, float, float, float]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError(
                f"projection must be a 4-component tuple, not {type(value)}: {value}"
            )

        # Don't try to set zero projection leading to division by zero
        width, height = self.window.get_size()
        if width == 0 or height == 0:
            return

        self.window.projection = Mat4.orthogonal_projection(
            value[0], value[1], value[2], value[3], -100, 100,
        )

    @property
    def projection_2d_matrix(self) -> Mat4:
        """
        Get the current projection matrix.
        This 4x4 float32 matrix is calculated when setting :py:attr:`~arcade.ArcadeContext.projection_2d`.

        This property simply gets and sets pyglet's projection matrix.

        :type: pyglet.math.Mat4
        """
        return self.window.projection

    @projection_2d_matrix.setter
    def projection_2d_matrix(self, value: Mat4):
        if not isinstance(value, Mat4):
            raise ValueError("projection_matrix must be a Mat4 object")

        self.window.projection = value

    @property
    def view_matrix_2d(self) -> Mat4:
        """
        Get the current view matrix.
        This 4x4 float32 matrix is calculated when setting :py:attr:`~arcade.ArcadeContext.view_matrix_2d`.

        This property simply gets and sets pyglet's view matrix.

        :type: pyglet.math.Mat4
        """
        self.window.view

    @view_matrix_2d.setter
    def view_matrix_2d(self, value: Mat4):
        if not isinstance(value, Mat4):
            raise ValueError("view_matrix must be a Mat4 object")

        self._view_matrix_2d = value
        self.window.view = self._view_matrix_2d

    @contextmanager
    def pyglet_rendering(self):
        """
        Context manager for doing rendering with pyglet
        ensuring context states are reverted. This
        affects things like blending.
        """
        blend_enabled = self.is_enabled(self.BLEND)
        try:
            yield
        finally:
            if blend_enabled:
                self.enable(self.BLEND)

    def load_program(
        self,
        *,
        vertex_shader: Union[str, Path],
        fragment_shader: Optional[Union[str, Path]] = None,
        geometry_shader: Optional[Union[str, Path]] = None,
        tess_control_shader: Optional[Union[str, Path]] = None,
        tess_evaluation_shader: Optional[Union[str, Path]] = None,
        common: Iterable[Union[str, Path]] = (),
        defines: Optional[Dict[str, Any]] = None,
        varyings: Optional[Sequence[str]] = None,
        varyings_capture_mode: str = "interleaved",
    ) -> Program:
        """
        Create a new program given a file names that contain the vertex shader and
        fragment shader. Note that fragment and geometry shader are optional for
        when transform shaders are loaded.

        This method also supports the resource handles.

        Example::

            # The most common use case if having a vertex and fragment shader
            program = window.ctx.load_program(
                vertex_shader="vert.glsl",
                fragment_shader="frag.glsl",
            )

        :param Union[str,pathlib.Path] vertex_shader: path to vertex shader
        :param Union[str,pathlib.Path] fragment_shader: path to fragment shader (optional)
        :param Union[str,pathlib.Path] geometry_shader: path to geometry shader (optional)
        :param Union[str,pathlib.Path] tess_control_shader: Tessellation Control Shader
        :param Union[str,pathlib.Path] tess_evaluation_shader: Tessellation Evaluation Shader
        :param List[Union[str,pathlib.Path]] common: Common files to be included in all shaders
        :param dict defines: Substitute ``#define`` values in the source
        :param Optional[Sequence[str]] varyings: The name of the out attributes in a transform shader.
                                                 This is normally not necessary since we auto detect them,
                                                 but some more complex out structures we can't detect.
        :param str varyings_capture_mode: The capture mode for transforms.
                                          ``"interleaved"`` means all out attribute will be written to a single buffer.
                                          ``"separate"`` means each out attribute will be written separate buffers.
                                          Based on these settings the `transform()` method will accept a single
                                          buffer or a list of buffer.
        """
        from arcade.resources import resolve

        vertex_shader_src = resolve(vertex_shader).read_text()
        fragment_shader_src = None
        geometry_shader_src = None
        tess_control_src = None
        tess_evaluation_src = None

        common_src = [resolve(c).read_text() for c in common]

        if fragment_shader:
            fragment_shader_src = resolve(fragment_shader).read_text()
            fragment_shader_src = self.shader_inc(fragment_shader_src)

        if geometry_shader:
            geometry_shader_src = resolve(geometry_shader).read_text()
            geometry_shader_src = self.shader_inc(geometry_shader_src)

        if tess_control_shader and tess_evaluation_shader:
            tess_control_src = resolve(tess_control_shader).read_text()
            tess_evaluation_src = resolve(
                tess_evaluation_shader
            ).read_text()
            tess_control_src = self.shader_inc(tess_control_src)
            tess_evaluation_src = self.shader_inc(tess_evaluation_src)

        return self.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src,
            geometry_shader=geometry_shader_src,
            tess_control_shader=tess_control_src,
            tess_evaluation_shader=tess_evaluation_src,
            common=common_src,
            defines=defines,
            varyings=varyings,
            varyings_capture_mode=varyings_capture_mode
        )

    def load_compute_shader(self, path: Union[str, Path], common: Iterable[Union[str, Path]] = ()) -> ComputeShader:
        """
        Loads a compute shader from file. This methods supports
        resource handles.

        Example::

            ctx.load_compute_shader(":shader:compute/do_work.glsl")

        :param Union[str,pathlib.Path] path: Path to texture
        :param Iterable[Union[str,pathlib.Path]] common: Common source injected into compute shader
        """
        from arcade.resources import resolve
        path = resolve(path)
        common_src = [resolve(c).read_text() for c in common]
        return self.compute_shader(
            source=self.shader_inc(path.read_text()),
            common=common_src,
        )

    def load_texture(
        self,
        path: Union[str, Path],
        *,
        flip: bool = True,
        build_mipmaps: bool = False,
    ) -> Texture2D:
        """
        Loads and creates an OpenGL 2D texture.
        Currently, all textures are converted to RGBA for simplicity.

        Example::

            # Load a texture in current working directory
            texture = window.ctx.load_texture("background.png")
            # Load a texture using Arcade resource handle
            texture = window.ctx.load_texture(":textures:background.png")

        :param Union[str,pathlib.Path] path: Path to texture
        :param bool flip: Flips the image upside down
        :param bool build_mipmaps: Build mipmaps for the texture
        """
        from arcade.resources import resolve

        path = resolve(path)

        image = Image.open(str(path))

        if flip:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        texture = self.texture(
            image.size, components=4, data=image.convert("RGBA").tobytes()
        )
        image.close()

        if build_mipmaps:
            texture.build_mipmaps()

        return texture

    def shader_inc(self, source: str) -> str:
        """
        Parse a shader source looking for ``#include`` directives and
        replace them with the contents of the included file.

        The ``#include`` directive must be on its own line and the file
        and the path should use a resource handle.

        Example::

            #include :my_shader:lib/common.glsl

        :param str source: Shader
        """
        from arcade.resources import resolve
        lines = source.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#include"):
                path = resolve(line.split()[1].replace('"', ""))
                lines[i] = path.read_text()
        return "\n".join(lines)

    def get_framebuffer_image(
        self,
        fbo: Framebuffer,
        components: int = 4,
        flip=True,
    ) -> Image.Image:
        """
        Shortcut method for reading data from a framebuffer and converting it to a PIL image.

        :param Framebuffer fbo: Framebuffer to get image from
        :param int components: Number of components to read
        :param bool flip: Flip the image upside down
        """
        mode = "RGBA"[:components]
        image = Image.frombuffer(
            mode,
            (fbo.width, fbo.height),
            fbo.read(components=components),
        )
        if flip:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        return image
