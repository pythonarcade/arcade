"""
Arcade's version of the OpenGL Context.
Contains pre-loaded programs
"""

from array import array
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import pyglet
from PIL import Image
from pyglet import gl
from pyglet.graphics.shader import UniformBufferObject
from pyglet.math import Mat4

import arcade
from arcade.camera import Projector
from arcade.camera.default import DefaultProjector
from arcade.gl import BufferDescription, Context
from arcade.gl.compute_shader import ComputeShader
from arcade.gl.framebuffer import Framebuffer
from arcade.gl.program import Program
from arcade.gl.texture import Texture2D
from arcade.gl.vertex_array import Geometry
from arcade.texture_atlas import DefaultTextureAtlas, TextureAtlasBase

__all__ = ["ArcadeContext"]


class ArcadeContext(Context):
    """
    An OpenGL context implementation for Arcade with added custom features.
    This context is normally accessed through :py:attr:`arcade.Window.ctx`.

    Args:
        window:
            The pyglet window
        gc_mode:
            The garbage collection mode for OpenGL objects. ``auto`` is just
            what we would expect in python while ``context_gc`` (default)
            requires you to call ``Context.gc()``. The latter can be useful
            when using multiple threads when it's not clear what thread will
            gc the object.
        gl_api:
            The OpenGL API to use. By default it's set to ``gl`` which is
            the standard OpenGL API. If you want to use OpenGL ES you can
            set it to ``gles``.
    """

    atlas_size: tuple[int, int] = 512, 512

    def __init__(
        self,
        window: pyglet.window.Window,  # type: ignore
        gc_mode: str = "context_gc",
        gl_api: str = "gl",
    ) -> None:
        super().__init__(window, gc_mode=gc_mode, gl_api=gl_api)

        # Set up a default orthogonal projection for sprites and shapes
        self._window_block: UniformBufferObject = window.ubo
        self.bind_window_block()

        self.blend_func = self.BLEND_DEFAULT

        self._default_camera: DefaultProjector = DefaultProjector(context=self)
        self.current_camera: Projector = self._default_camera

        self.viewport = (0, 0, window.width, window.height)

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

        self.sprite_list_program_no_geo = self.load_program(
            vertex_shader=":system:shaders/sprites/sprite_list_simple_vs.glsl",
            fragment_shader=":system:shaders/sprites/sprite_list_simple_fs.glsl",
        )
        self.sprite_list_program_no_geo["sprite_texture"] = 0
        self.sprite_list_program_no_geo["uv_texture"] = 1
        # Per-instance data
        self.sprite_list_program_no_geo["pos_data"] = 2
        self.sprite_list_program_no_geo["size_data"] = 3
        self.sprite_list_program_no_geo["color_data"] = 4
        self.sprite_list_program_no_geo["texture_id_data"] = 5
        self.sprite_list_program_no_geo["index_data"] = 6

        # Geo shader single sprite program
        self.sprite_program_single = self.load_program(
            vertex_shader=":system:shaders/sprites/sprite_single_vs.glsl",
            geometry_shader=":system:shaders/sprites/sprite_list_geometry_no_cull_geo.glsl",
            fragment_shader=":system:shaders/sprites/sprite_list_geometry_fs.glsl",
        )
        self.sprite_program_single["sprite_texture"] = 0
        self.sprite_program_single["uv_texture"] = 1
        self.sprite_program_single["spritelist_color"] = 1.0, 1.0, 1.0, 1.0
        # Non-geometry shader single sprite program
        self.sprite_program_single_simple = self.load_program(
            vertex_shader=":system:shaders/sprites/sprite_single_simple_vs.glsl",
            fragment_shader=":system:shaders/sprites/sprite_list_simple_fs.glsl",
        )
        self.sprite_program_single_simple["sprite_texture"] = 0
        self.sprite_program_single_simple["uv_texture"] = 1
        self.sprite_program_single_simple["spritelist_color"] = 1.0, 1.0, 1.0, 1.0

        # fmt: off
        self.spritelist_geometry_simple = self.geometry(
            [
                BufferDescription(
                    self.buffer(
                        data=array("f", [
                            -0.5, +0.5,  # Upper left
                            -0.5, -0.5,  # lower left
                            +0.5, +0.5,  # upper right
                            +0.5, -0.5,  # lower right
                        ])
                    ),
                    "2f",
                    ["in_pos"]
                ),
            ],
            mode=self.TRIANGLE_STRIP,
        )
        # fmt: on

        # Shapes
        self.shape_line_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/line/unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/line/unbuffered_fs.glsl",
        )
        self.shape_ellipse_filled_unbuffered_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/ellipse/filled_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/ellipse/filled_unbuffered_fs.glsl",
        )
        self.shape_ellipse_outline_unbuffered_program: Program = self.load_program(
            vertex_shader=":system:shaders/shapes/ellipse/outline_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/ellipse/outline_unbuffered_fs.glsl",
        )
        self.shape_rectangle_filled_unbuffered_program = self.load_program(
            vertex_shader=":system:shaders/shapes/rectangle/filled_unbuffered_vs.glsl",
            fragment_shader=":system:shaders/shapes/rectangle/filled_unbuffered_fs.glsl",
        )

        # Atlas shaders
        self.atlas_resize_program: Program = self.load_program(
            # NOTE: This is the geo shader version of the atlas resize program.
            # vertex_shader=":system:shaders/atlas/resize_vs.glsl",
            # geometry_shader=":system:shaders/atlas/resize_gs.glsl",
            # fragment_shader=":system:shaders/atlas/resize_fs.glsl",
            # Vertex and fragment shader version
            vertex_shader=":system:shaders/atlas/resize_simple_vs.glsl",
            fragment_shader=":system:shaders/atlas/resize_simple_fs.glsl",
        )
        self.atlas_resize_program["atlas_old"] = 0  # Configure texture channels
        self.atlas_resize_program["atlas_new"] = 1
        self.atlas_resize_program["texcoords_old"] = 2
        self.atlas_resize_program["texcoords_new"] = 3

        # NOTE: These should not be created when WebGL is used
        # SpriteList collision resources
        # Buffer version of the collision detection program.
        self.collision_detection_program = self.load_program(
            vertex_shader=":system:shaders/collision/col_trans_vs.glsl",
            geometry_shader=":system:shaders/collision/col_trans_gs.glsl",
        )
        # Texture version of the collision detection program.
        self.collision_detection_program_simple = self.load_program(
            vertex_shader=":system:shaders/collision/col_tex_trans_vs.glsl",
            geometry_shader=":system:shaders/collision/col_tex_trans_gs.glsl",
        )
        self.collision_detection_program_simple["pos_angle_data"] = 0
        self.collision_detection_program_simple["size_data"] = 1
        self.collision_detection_program_simple["index_data"] = 2

        self.collision_buffer = self.buffer(reserve=1024 * 4)
        self.collision_query = self.query(samples=False, time=False, primitives=True)

        # General Utility

        # renders a quad (without projection) with a single 4-component texture.
        self.utility_textured_quad_program: Program = self.load_program(
            vertex_shader=":system:shaders/util/textured_quad_vs.glsl",
            fragment_shader=":system:shaders/util/textured_quad_fs.glsl",
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
                ),
            ]
        )
        # Shape line(s)
        self.shape_line_buffer_pos = self.buffer(reserve=8 * 10)
        self.shape_line_geometry = self.geometry(
            [
                # Instanced quad (triangle strip)
                BufferDescription(
                    self.buffer(
                        data=array(
                            "f",
                            [
                                0.0,  # 4 dummy vertices
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                            ],
                        )
                    ),
                    "2f",
                    ["in_vert"],
                ),
                BufferDescription(
                    self.shape_line_buffer_pos, "4f", ["in_instance_pos"], instanced=True
                ),
            ],
            mode=self.TRIANGLE_STRIP,
        )
        # ellipse/circle filled. Empty geometry. We generate it on the fly in the vertex shader.
        self.shape_ellipse_unbuffered_geometry: Geometry = self.geometry()
        # ellipse/circle outline. Empty geometry. We generate it on the fly in the vertex shader.
        self.shape_ellipse_outline_unbuffered_geometry: Geometry = self.geometry()
        # rectangle filled
        self.shape_rectangle_filled_unbuffered_buffer = self.buffer(reserve=8)
        # fmt: off
        self.shape_rectangle_filled_unbuffered_geometry: Geometry = self.geometry(
            [
                # Instanced quad (triangle strip)
                BufferDescription(
                    self.buffer(
                        data=array(
                            "f",
                            [
                                -0.5, +0.5,  # Upper left
                                -0.5, -0.5,  # lower left
                                +0.5, +0.5,  # upper right
                                +0.5, -0.5,  # lower right
                            ],
                        )
                    ),
                    "2f",
                    ["in_vert"],
                ),
                # Per instance data
                BufferDescription(
                    self.shape_rectangle_filled_unbuffered_buffer,
                    "2f",
                    ["in_instance_pos"],
                    instanced=True
                ),
            ],
            mode=self.TRIANGLE_STRIP,
        )
        # fmt: on
        self.geometry_empty: Geometry = self.geometry()

        self._atlas: TextureAtlasBase | None = None
        # Global labels we modify in `arcade.draw_text`.
        # These multiple labels with different configurations are stored
        self.label_cache: dict[str, arcade.Text] = {}

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
        self.viewport = 0, 0, self.window.width, self.window.height
        self.view_matrix = Mat4()
        self.projection_matrix = Mat4.orthogonal_projection(
            0, self.window.width, 0, self.window.height, -100, 100
        )
        self.enable_only(self.BLEND)
        self.blend_func = self.BLEND_DEFAULT
        self.point_size = 1.0

    def bind_window_block(self) -> None:
        """
        Binds the global projection and view uniform buffer object.

        This should always be bound to index 0 so all shaders
        have access to them.
        """
        gl.glBindBufferRange(
            gl.GL_UNIFORM_BUFFER,
            0,
            self._window_block.buffer.id,
            0,  # type: ignore
            128,  # 32 x 32bit floats (two mat4) # type: ignore
        )

    @property
    def default_atlas(self) -> TextureAtlasBase:
        """
        The default texture atlas.

        This is created when Arcade is initialized.
        All sprite lists will use use this atlas unless a different atlas
        is passed in the :py:class:`arcade.SpriteList` constructor.
        """
        if not self._atlas:
            # Create the default texture atlas
            # 8192 is a safe maximum size for textures in OpenGL 3.3
            # We might want to query the max limit, but this makes it consistent
            # across all OpenGL implementations.
            self._atlas = DefaultTextureAtlas(
                self.atlas_size,
                border=2,
                auto_resize=True,
                ctx=self,
            )

        return self._atlas

    @property
    def viewport(self) -> tuple[int, int, int, int]:
        """
        Get or set the viewport for the currently active framebuffer.

        The viewport simply describes what pixels of the screen
        OpenGL should render to. Format is ``(x, y, width, height)``.
        Normally it would be the size of the window's framebuffer::

            # 4:3 screen
            ctx.viewport = 0, 0, 800, 600
            # 1080p
            ctx.viewport = 0, 0, 1920, 1080
            # Using the current framebuffer size
            ctx.viewport = 0, 0, *ctx.screen.size
        """
        return self.active_framebuffer.viewport

    @viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
        self.active_framebuffer.viewport = value
        if self._default_camera == self.current_camera:
            self._default_camera.use()

    @property
    def projection_matrix(self) -> Mat4:
        """
        Get or set the current projection matrix.

        This 4x4 float32 matrix is usually calculated by a cameras but
        can be modified directly if you know what you are doing.

        This property simply gets and sets pyglet's projection matrix.
        """
        return self.window.projection

    @projection_matrix.setter
    def projection_matrix(self, value: Mat4):
        if not isinstance(value, Mat4):
            raise ValueError("projection_matrix must be a Mat4 object")

        self.window.projection = value

    @property
    def view_matrix(self) -> Mat4:
        """
        Get or set the current view matrix.

        This 4x4 float32 matrix is usually calculated by a cameras but
        can be modified directly if you know what you are doing.

        This property simply gets and sets pyglet's view matrix.
        """
        return self.window.view

    @view_matrix.setter
    def view_matrix(self, value: Mat4):
        if not isinstance(value, Mat4):
            raise ValueError("view_matrix must be a Mat4 object")

        self.window.view = value

    def load_program(
        self,
        *,
        vertex_shader: str | Path,
        fragment_shader: str | Path | None = None,
        geometry_shader: str | Path | None = None,
        tess_control_shader: str | Path | None = None,
        tess_evaluation_shader: str | Path | None = None,
        common: Iterable[str | Path] = (),
        defines: dict[str, Any] | None = None,
        varyings: Sequence[str] | None = None,
        varyings_capture_mode: str = "interleaved",
    ) -> Program:
        """
        Create a new program given file names that contain the vertex shader and
        fragment shader. Note that the fragment and geometry shaders are optional
        when transform shaders are loaded.

        This method also supports resource handles.

        Example::

            # The most common use case is having a vertex and fragment shader
            program = window.ctx.load_program(
                vertex_shader="vert.glsl",
                fragment_shader="frag.glsl",
            )

        Args:
            vertex_shader:
                Path to the vertex shader.
            fragment_shader:
                Path to the fragment shader.
            geometry_shader:
                Path to the geometry shader.
            tess_control_shader:
                Tessellation Control Shader.
            tess_evaluation_shader:
                Tessellation Evaluation Shader.
            common:
                Common files to be included in all shaders.
            defines:
                Substitute `#define` values in the source.
            varyings:
                The name of the out attributes in a transform shader.
                This is normally not necessary since we auto detect them,
                but some more complex out structures we can't detect.
            varyings_capture_mode:
                The capture mode for transforms.

                Based on these settings, the `transform()` method will accept a single
                buffer or a list of buffers.

                - ``"interleaved"`` means all out attributes will be written to a single buffer.
                - ``"separate"`` means each out attribute will be written to separate buffers.
        """
        from arcade.resources import resolve

        vertex_shader_src = resolve(vertex_shader).read_text()
        vertex_shader_src = self.shader_inc(vertex_shader_src)

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
            tess_evaluation_src = resolve(tess_evaluation_shader).read_text()
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
            varyings_capture_mode=varyings_capture_mode,
        )

    def load_compute_shader(
        self, path: str | Path, common: Iterable[str | Path] = ()
    ) -> ComputeShader:
        """
        Loads a compute shader from file. This methods supports
        resource handles.

        Example::

            ctx.load_compute_shader(":shader:compute/do_work.glsl")

        Args:
            path:
                Path to texture
            common:
                Common sources injected into compute shader
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
        path: str | Path,
        *,
        flip: bool = True,
        wrap_x=None,
        wrap_y=None,
        filter=None,
        build_mipmaps: bool = False,
        internal_format: int | None = None,
        immutable: bool = False,
        compressed: bool = False,
    ) -> Texture2D:
        """
        Loads and creates an OpenGL 2D texture.
        Currently, all textures are converted to RGBA for simplicity.

        Examples::

            # Load a texture in current working directory
            texture = window.ctx.load_texture("background.png")

            # Load a texture using Arcade resource handle
            texture = window.ctx.load_texture(":textures:background.png")

            # Load and compress a texture
            texture = window.ctx.load_texture(
                ":textures:background.png",
                internal_format=gl.GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,
                compressed=True,
            )

        Args:
            path:
                Path to texture
            flip:
                Flips the image upside down. Default is ``True``.
            wrap_x:
                The wrap mode for the x-axis. Default is ``None``.
            wrap_y:
                The wrap mode for the y-axis. Default is ``None``.
            filter:
                The min and mag filter. Default is ``None``.
            build_mipmaps:
                Build mipmaps for the texture. Default is ``False``.
            internal_format:
                The internal format of the texture. This can be used to override
                the default internal format when using sRGBA or compressed textures.
            immutable:
                Make the storage (not the contents) immutable. This can sometimes be
                required when using textures with compute shaders.
            compressed:
                If the internal format is a compressed format meaning your
                texture will be compressed by the GPU.
        """
        from arcade.resources import resolve

        path = resolve(path)

        image: Image.Image = Image.open(str(path))  # type: ignore

        if flip:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        texture = self.texture(
            image.size,
            components=4,
            data=image.convert("RGBA").tobytes(),
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
            internal_format=internal_format,
            immutable=immutable,
            compressed=compressed,
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

            #include :my_resource_handle:lib/common.glsl

        Args:
            source: The shader source code
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
        flip: bool = True,
    ) -> Image.Image:
        """
        Shortcut method for reading data from a framebuffer and converting it to a PIL image.

        Args:
            fbo:
                Framebuffer to get image from
            components:
                Number of components to read. Default is 4 (RGBA).
                Valid values are 1, 2, 3, 4.
            flip:
                Flip the image upside down. This is useful because OpenGL has the
                origin at the bottom left corner while PIL has it at the top left.
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
