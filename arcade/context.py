"""
Arcade's version of the OpenGL Context.
Contains pre-loaded programs 
"""
from pathlib import Path
from typing import Union
from arcade.gl import BufferDescription, Context
from arcade.gl.program import Program


class ArcadeContext(Context):
    """
    Represents an OpenGL context. This context belongs to an arcade.Window.
    """

    def __init__(self, window):
        super().__init__(window)

        # --- Pre-load system shaders here ---
        # FIXME: These pre-created resources needs to be packaged nicely
        #        Just having them globally in the context is probably not a good idea
        self.line_vertex_shader = self.load_program(
            vertex_shader=':resources:shaders/shapes/line/line_vertex_shader_vs.glsl',
            fragment_shader=':resources:shaders/shapes/line/line_vertex_shader_fs.glsl',
        )
        self.line_generic_with_colors_program = self.load_program(
            vertex_shader=':resources:shaders/shapes/line/line_generic_with_colors_vs.glsl',
            fragment_shader=':resources:shaders/shapes/line/line_generic_with_colors_fs.glsl',
        )
        self.shape_element_list_program = self.load_program(
            vertex_shader=':resources:shaders/shape_element_list_vs.glsl',
            fragment_shader=':resources:shaders/shape_element_list_fs.glsl',
        )
        # self.sprite_list_program = self.load_program(
        #     vertex_shader=':resources:shaders/sprites/sprite_list_instanced_vs.glsl',
        #     fragment_shader=':resources:shaders/sprites/sprite_list_instanced_fs.glsl',
        # )
        self.sprite_list_program_no_cull = self.load_program(
            vertex_shader=':resources:shaders/sprites/sprite_list_geometry_vs.glsl',
            geometry_shader=':resources:shaders/sprites/sprite_list_geometry_no_cull_geo.glsl',
            fragment_shader=':resources:shaders/sprites/sprite_list_geometry_fs.glsl',
        )
        self.sprite_list_program_cull = self.load_program(
            vertex_shader=':resources:shaders/sprites/sprite_list_geometry_vs.glsl',
            geometry_shader=':resources:shaders/sprites/sprite_list_geometry_cull_geo.glsl',
            fragment_shader=':resources:shaders/sprites/sprite_list_geometry_fs.glsl',
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
        self.generic_draw_line_strip_geometry = self.geometry([
                BufferDescription(self.generic_draw_line_strip_vbo, '2f', ['in_vert']),
                BufferDescription(self.generic_draw_line_strip_color, '4f1', ['in_color'], normalized=['in_color'])])
        # Shape line(s)
        # Reserve space for 1000 lines (2f pos, 4f color)
        # TODO: Different version for buffered and unbuffered
        # TODO: Make round-robin buffers
        self.shape_line_buffer_pos = self.buffer(reserve=8 * 10)
        # self.shape_line_buffer_color = self.buffer(reserve=4 * 10)
        self.shape_line_geometry = self.geometry([
            BufferDescription(self.shape_line_buffer_pos, '2f', ['in_vert']),
            # BufferDescription(self.shape_line_buffer_color, '4f1', ['in_color'], normalized=['in_color'])
        ])
        # ellipse/circle filled
        self.shape_ellipse_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_ellipse_unbuffered_geometry = self.geometry([
            BufferDescription(self.shape_ellipse_unbuffered_buffer, '2f', ['in_vert'])])
        # ellipse/circle outline
        self.shape_ellipse_outline_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_ellipse_outline_unbuffered_geometry = self.geometry([
            BufferDescription(self.shape_ellipse_outline_unbuffered_buffer, '2f', ['in_vert'])])
        # rectangle filled
        self.shape_rectangle_filled_unbuffered_buffer = self.buffer(reserve=8)
        self.shape_rectangle_filled_unbuffered_geometry = self.geometry([
            BufferDescription(self.shape_rectangle_filled_unbuffered_buffer, '2f', ['in_vert'])])

    def load_program(
            self,
            *,
            vertex_shader: Union[str, Path],
            fragment_shader: Union[str, Path] = None,
            geometry_shader: Union[str, Path] = None,
            defines: dict = None) -> Program:
        """Create a new program given a file names that contain the vertex shader and
        fragment shader.

        :param Union[str, Path] vertex_shader: path to vertex shader
        :param Union[str, Path] fragment_shader: path to fragment shader
        :param Union[str, Path] geometry_shader: path to geometry shader
        :param dict defines: Substitute #defines values in the source
        """
        from arcade.resources import resolve_resource_path

        vertex_shader_src = resolve_resource_path(vertex_shader).read_text()
        fragment_shader_src = None
        geometry_shader_src = None

        if fragment_shader:
            fragment_shader_src = resolve_resource_path(fragment_shader).read_text()

        if geometry_shader:
            geometry_shader_src = resolve_resource_path(geometry_shader).read_text()

        return self.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src,
            geometry_shader=geometry_shader_src,
            defines=defines,
        )
