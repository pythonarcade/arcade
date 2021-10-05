"""
Shadertoy

Inputs:

uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform float     iTime;                 // shader playback time (in seconds)
uniform float     iTimeDelta;            // render time (in seconds)
uniform int       iFrame;                // shader playback frame
uniform float     iChannelTime[4];       // channel playback time (in seconds)
uniform vec3      iChannelResolution[4]; // channel resolution (in pixels)
uniform vec4      iMouse;                // mouse pixel coords. xy: current (if MLB down), zw: click
uniform samplerXX iChannel0..3;          // input channel. XX = 2D/Cube
uniform vec4      iDate;                 // (year, month, day, time in seconds)
uniform float     iSampleRate;           // sound sample rate (i.e., 44100)
"""
from arcade.gl.framebuffer import Framebuffer
import string
from pathlib import Path
from typing import Tuple, Optional, Union

from arcade import get_window
import arcade
from arcade.context import ArcadeContext
from arcade.gl import geometry, Texture


class ShadertoyBase:
    """
    Base class for shadertoy types.
    It can represent the main image or buffers.
    """
    def __init__(self, size: Tuple[int, int], source: str):
        self._ctx = get_window().ctx
        self._size = size
        self._source = source
        # Uniforms
        self._mouse_pos = 0.0, 0.0
        self._time: float = 0.0
        self._time_delta: float = 0.0
        self._frame: int = 0
        # Shader inputs
        self._channel_0: Optional[Texture] = None
        self._channel_1: Optional[Texture] = None
        self._channel_2: Optional[Texture] = None
        self._channel_3: Optional[Texture] = None

        self._set_source(source)
        self._quad = geometry.quad_2d_fs()

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get or set the size in pixels
        """
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def time(self) -> float:
        """
        Get or set the current time
        """
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def time_delta(self) -> float:
        """
        Get or set the current delta time
        """
        return self._time_delta

    @time_delta.setter
    def time_delta(self, value):
        self._time_delta = value

    @property
    def frame(self) -> int:
        """
        Get or set the current frame
        """
        return self._frame

    @frame.setter
    def frame(self, value):
        self._frame = value

    @property
    def mouse_position(self) -> Tuple[float, float]:
        """
        Get or set the current mouse position
        """
        return self._mouse_pos

    @mouse_position.setter
    def mouse_position(self, value):
        self._mouse_pos = value

    @property
    def channel_0(self) -> Optional[Texture]:
        """Get or set channel 0"""
        return self._channel_0        

    @channel_0.setter
    def channel_0(self, value: Texture):
        if not isinstance(value, Texture):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_0 = value

    @property
    def channel_1(self) -> Optional[Texture]:
        """Get or set channel 1"""
        return self._channel_1

    @channel_1.setter
    def channel_1(self, value: Texture):
        if not isinstance(value, Texture):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_1 = value

    @property
    def channel_2(self) -> Optional[Texture]:
        """Get or set channel 2"""
        return self._channel_2        

    @channel_2.setter
    def channel_2(self, value: Texture):
        if not isinstance(value, Texture):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_2 = value

    @property
    def channel_3(self) -> Optional[Texture]:
        """Get or set channel 3"""
        return self._channel_3

    @channel_3.setter
    def channel_3(self, value: Texture):
        if not isinstance(value, Texture):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_3 = value

    @property
    def program(self):
        return self._program

    @property
    def ctx(self) -> ArcadeContext:
        return self._ctx

    def resize(self, size: Tuple[int, int]):
        raise NotImplementedError

    def render(
        self,
        *,
        time: Optional[float] = None,
        time_delta: Optional[float] = None,
        mouse_position: Optional[Tuple[float, float]] = None,
        size: Optional[Tuple[int, int]] = None,
        frame: Optional[int] = None,
    ):
        """Render the shadertoy project to the screen"""
        self._time = time if time is not None else self._time
        self._time_delta = time_delta if time_delta is not None else self._time_delta
        self._mouse_pos = mouse_position if mouse_position is not None else self._mouse_pos
        self._size = size if size is not None else self._size
        self._frame = frame if frame is not None else self._frame
        self._render()

    def _render(self):
        raise NotImplementedError        

    def reload(self, source: str):
        """Update the shader source code"""
        self._set_source(source)

    def _bind_channels(self):
        if self._channel_0:
            self._channel_0.use(0)
        if self._channel_1:
            self._channel_1.use(1)
        if self._channel_2:
            self._channel_2.use(2)
        if self._channel_3:
            self._channel_3.use(3)

    def _set_uniforms(self):
        """Attempt to set all supported uniforms"""
        try:
            self._program['iTime'] = self._time
        except KeyError:
            pass
        try:
            self._program['iTimeDelta'] = self._time_delta
        except KeyError:
            pass
        try:
            self._program['iMouse'] = self._mouse_pos[0], self._mouse_pos[1]
        except KeyError:
            pass
        try:
            self._program['iResolution'] = self._size
        except KeyError:
            pass
        try:
            self._program['iFrame'] = self._frame
        except KeyError:
            pass

    def _set_source(self, source: str):
        """
        Load shader templates, injects main function,
        create program and configures the program.
        """
        vs_path = arcade.resources.resolve_resource_path(":resources:shaders/shadertoy/base_vs.glsl")
        fs_path = arcade.resources.resolve_resource_path(":resources:shaders/shadertoy/base_fs.glsl")
        with open(vs_path) as fd:
            vs_source = fd.read()
        with open(fs_path) as fd:
            fs_source = fd.read()

        template = string.Template(fs_source)

        self._program = self.ctx.program(
            vertex_shader=vs_source,
            fragment_shader=template.substitute({"mainfunc": source}),
        )
        # Configure texture channels
        for channel in [0, 1, 2, 3]:
            try:
                self._program[f"iChannel{channel}"] = channel
            except KeyError:
                pass        
        self._source = source


class ShadertoyBuffer(ShadertoyBase):
    """
    An offscreen framebuffer we can render to with the supplied
    shader or render any other content into. 
    """

    def __init__(self, size: Tuple[int, int], source: str, repeat: bool = False):
        super().__init__(size, source)
        self._texture = self.ctx.texture(self._size, components=4)
        self._fbo = self.ctx.framebuffer(color_attachments=[self._texture])
        self._repeat = repeat
        self._set_repeat()

    @property
    def texture(self) -> Texture:
        """
        The OpenGL texture for this buffer.
        This can be assigned to channels.
        """
        return self._texture

    @property
    def fbo(self) -> Framebuffer:
        return self._fbo

    @property
    def repeat(self) -> bool:
        return self._repeat

    @repeat.setter
    def repeat(self, value: bool):
        self._repeat = value
        self._set_repeat()

    def clear(self):
        """Clear the buffer contents"""
        self._fbo.clear()

    def _set_repeat(self):
        if self._repeat:
            self._texture.wrap_x = self.ctx.REPEAT
            self._texture.wrap_y = self.ctx.REPEAT
        else:
            self._texture.wrap_x = self.ctx.CLAMP_TO_EDGE
            self._texture.wrap_y = self.ctx.CLAMP_TO_EDGE

    def _render(self):
        self._bind_channels()
        self._set_uniforms()
        with self._fbo.activate():
            self._quad.render(self._program)

    def resize(self, size: Tuple[int, int]):
        """Resize the internal texture"""
        if self._size == size:
            return
        self._size = size
        # Resize the internal texture and fbo + clear
        self._texture.resize((self._size))
        self._fbo.resize()
        self._fbo.clear()


class Shadertoy(ShadertoyBase):
    """A ShaderToy interface for arcade.

    Simply implement the ``mainImage`` glsl method::

        void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
            fragColor = vec4(fragCoord, 0.0, 1.0);
        }
    """
    def __init__(self, size: Tuple[int, int], main_source: str):
        """
        :param [int, int] size: pixel size if the output
        :param str main_source: The main glsl source with mainImage function
        """
        super().__init__(size, main_source)

        self._buffer_a: Optional[ShadertoyBuffer] = None
        self._buffer_b: Optional[ShadertoyBuffer] = None
        self._buffer_c: Optional[ShadertoyBuffer] = None
        self._buffer_d: Optional[ShadertoyBuffer] = None

    @property
    def buffer_a(self) -> Optional[ShadertoyBuffer]:
        """Get or set buffer a"""
        return self._buffer_a

    @buffer_a.setter
    def buffer_a(self, value):
        self._buffer_a = value

    @property
    def buffer_b(self) -> Optional[ShadertoyBuffer]:
        """Get or set buffer b"""
        return self._buffer_b

    @buffer_b.setter
    def buffer_b(self, value):
        self._buffer_b = value

    @property
    def buffer_c(self) -> Optional[ShadertoyBuffer]:
        """Get or set buffer c"""
        return self._buffer_c

    @buffer_c.setter
    def buffer_c(self, value):
        self._buffer_c = value

    @property
    def buffer_d(self) -> Optional[ShadertoyBuffer]:
        """Get or set buffer d"""
        return self._buffer_d

    @buffer_d.setter
    def buffer_d(self, value):
        self._buffer_d = value

    @classmethod
    def create_from_file(cls, size: Tuple[int, int], path: Union[str, Path]) -> "Shadertoy":
        path = arcade.resources.resolve_resource_path(path)
        with open(path) as fd:
            source = fd.read()
        return cls(size, source)

    def create_buffer(self, source, repeat: bool = False) -> ShadertoyBuffer:
        """
        Shortcut for creating a buffer.
        """
        return ShadertoyBuffer(self._size, source, repeat=repeat)

    def create_buffer_from_file(self, path: Union[str, Path]) -> ShadertoyBuffer:
        """
        Shortcut for creating a buffer.
        """
        path = arcade.resources.resolve_resource_path(path)
        with open(path) as fd:
            source = fd.read()
        return ShadertoyBuffer(self._size, source)

    def resize(self, size: Tuple[int, int]):
        """
        Resize the internal buffers

        :param Tuple[int,int] size: The new size in pixels
        """
        self._size = size

        if self._buffer_a:
            self._buffer_a.resize(size)
        if self._buffer_b:
            self._buffer_b.resize(size)
        if self._buffer_c:
            self._buffer_c.resize(size)
        if self._buffer_d:
            self._buffer_d.resize(size)

    def _render(self):
        # Render buffers first
        # with self.ctx.enabled_only():
        buffers = [self._buffer_a, self._buffer_b, self._buffer_c, self._buffer_d]
        for buffer in buffers:
            if buffer is not None:
                buffer.render(
                    time=self._time,
                    time_delta=self._time_delta,
                    mouse_position=self._mouse_pos,
                    size=self._size,
                    frame=self._frame,
                )

        # Run the main program
        self._bind_channels()
        self._set_uniforms()
        self._quad.render(self._program)
