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

import string
from datetime import datetime
from pathlib import Path

import arcade
from arcade import get_window
from arcade.context import ArcadeContext
from arcade.gl import Texture2D, geometry
from arcade.gl.framebuffer import Framebuffer
from arcade.gl.program import Program


class ShadertoyBase:
    """
    Base class for shadertoy types.
    It can represent the main image or buffers.

    Supported uniforms are::

        uniform float     iTime;                 // shader playback time (in seconds)
        uniform float     iChannelTime[4];       // channel playback time (in seconds)
        uniform vec4      iMouse;                // mouse pixel coords. xy: current (if MLB down)
                                                   zw: click
        uniform vec3      iResolution;           // viewport resolution (in pixels)
        uniform vec3      iChannelResolution[4]; // channel resolution (in pixels)
        uniform int       iFrame;                // shader playback frame
        uniform float     iTimeDelta;            // render time (in seconds)
        uniform vec4      iDate;                 // (year, month, day, time in seconds)
        // Channel textures
        uniform sampler2D iChannel0;
        uniform sampler2D iChannel1;
        uniform sampler2D iChannel2;
        uniform sampler2D iChannel3;

    Args:
        size:
            screen/area size
        source:
            The mainImage shader source
    """

    def __init__(self, size: tuple[int, int], source: str):
        self._ctx = get_window().ctx
        self._size = size
        self._source = source
        # Uniforms
        self._mouse_pos = 0.0, 0.0
        self._mouse_buttons = 0.0, 0.0
        self._time: float = 0.0
        self._time_delta: float = 0.0
        self._frame: int = 0
        self._frame_rate: float = 0.0
        self._channel_time = [0.0, 0.0, 0.0, 0.0]
        self._channel_resolution = [0] * 3 * 4
        # Shader inputs
        self._channel_0: Texture2D | None = None
        self._channel_1: Texture2D | None = None
        self._channel_2: Texture2D | None = None
        self._channel_3: Texture2D | None = None

        self._set_source(source)
        self._quad = geometry.quad_2d_fs()

    @property
    def size(self) -> tuple[int, int]:
        """
        Get or set the size in pixels.

        Mapped to uniform ``iResolution.xy``.
        """
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def time(self) -> float:
        """
        Get or set the current time.

        Mapped to uniform ``iTime``.
        """
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def time_delta(self) -> float:
        """
        Get or set the current delta time.

        Mapped to uniform ``iTimeDelta``.
        """
        return self._time_delta

    @time_delta.setter
    def time_delta(self, value):
        self._time_delta = value

    @property
    def delta_time(self) -> float:
        """
        Get or set the current delta time.
        An alternative to ``time_delta``.

        Mapped to uniform ``iTimeDelta``.
        """
        return self._time_delta

    @delta_time.setter
    def delta_time(self, value):
        self._time_delta = value

    @property
    def frame(self) -> int:
        """
        Get or set the current frame.

        Mapped to uniform ``iFrame``.
        """
        return self._frame

    @frame.setter
    def frame(self, value):
        self._frame = value

    @property
    def frame_rate(self) -> float:
        """
        Get or set the frame rate.

        Mapped to uniform ``iFrameRate``.
        """
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, value: float):
        self._frame_rate = value

    @property
    def mouse_position(self) -> tuple[float, float]:
        """
        Get or set the current mouse position.

        Mapped to uniform ``iMouse.xy``.
        """
        return self._mouse_pos

    @mouse_position.setter
    def mouse_position(self, value):
        self._mouse_pos = value

    @property
    def mouse_buttons(self) -> tuple[float, float]:
        """
        Get or set the mouse button states.
        Depending on the use case these can contain
        a non-zero value when buttons are pushed and/or
        the actual click position.

        Mapped to uniform ``iMouse.zw``.
        """
        return self._mouse_buttons

    @mouse_buttons.setter
    def mouse_buttons(self, value: tuple[float, float]):
        self._mouse_buttons = value

    @property
    def channel_time(self) -> list[float]:
        return self._channel_time

    @property
    def channel_0(self) -> Texture2D | None:
        """Get or set channel 0"""
        return self._channel_0

    @channel_0.setter
    def channel_0(self, value: Texture2D):
        if not isinstance(value, Texture2D):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_resolution[0:3] = value.width, value.height, 1
        self._channel_0 = value

    @property
    def channel_1(self) -> Texture2D | None:
        """Get or set channel 1"""
        return self._channel_1

    @channel_1.setter
    def channel_1(self, value: Texture2D):
        if not isinstance(value, Texture2D):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_resolution[3:6] = value.width, value.height, 1
        self._channel_1 = value

    @property
    def channel_2(self) -> Texture2D | None:
        """Get or set channel 2"""
        return self._channel_2

    @channel_2.setter
    def channel_2(self, value: Texture2D):
        if not isinstance(value, Texture2D):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_resolution[6:9] = value.width, value.height, 1
        self._channel_2 = value

    @property
    def channel_3(self) -> Texture2D | None:
        """Get or set channel 3"""
        return self._channel_3

    @channel_3.setter
    def channel_3(self, value: Texture2D):
        if not isinstance(value, Texture2D):
            raise ValueError("A channel only accepts an arcade.gl.Texture")
        self._channel_resolution[9:12] = value.width, value.height, 1
        self._channel_3 = value

    @property
    def program(self) -> Program:
        """The shader program"""
        return self._program

    @property
    def ctx(self) -> ArcadeContext:
        """The context"""
        return self._ctx

    def resize(self, size: tuple[int, int]) -> None:
        """Resize of this shadertoy or buffer"""
        raise NotImplementedError

    def render(
        self,
        *,
        time: float | None = None,
        time_delta: float | None = None,
        mouse_position: tuple[float, float] | None = None,
        size: tuple[int, int] | None = None,
        frame: int | None = None,
        frame_rate: float | None = None,
    ):
        """
        Render the shadertoy project to the screen.

        Args:
            time:
                Override the time
            time_delta:
                Override the time delta
            mouse_position:
                Override mouse position
            size:
                Override the size
            frame:
                Override frame
            frame_rate:
                Override frame_rate
        """
        self._time = time if time is not None else self._time
        self._time_delta = time_delta if time_delta is not None else self._time_delta
        self._mouse_pos = mouse_position if mouse_position is not None else self._mouse_pos
        self._size = size if size is not None else self._size
        self._frame = frame if frame is not None else self._frame
        self._frame_rate = frame_rate if frame_rate is not None else self._frame_rate
        self._render()

    def _render(self):
        raise NotImplementedError

    def reload(self, source: str):
        """
        Update the shader source code.

        Args:
            source: New mainImage shader source
        """
        self._set_source(source)

    def _bind_channels(self):
        """Bind channel textures if set"""
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
        self._program.set_uniform_safe("iTime", self._time)
        self._program.set_uniform_array_safe("iChannelTime", self._channel_time)
        self._program.set_uniform_safe("iTimeDelta", self._time_delta)
        self._program.set_uniform_safe("iMouse", (*self._mouse_pos, *self._mouse_buttons))
        self._program.set_uniform_safe("iResolution", (*self._size, 1.0))
        self._program.set_uniform_array_safe("iChannelResolution", self._channel_resolution)
        self._program.set_uniform_safe("iFrame", self._frame)
        self._program.set_uniform_safe("iFrameRate", self._frame_rate)
        self._program.set_uniform_safe("iDate", self._get_date())

    def _get_date(self) -> tuple[float, float, float, float]:
        """Create year, month, day, seconds data for iDate"""
        now = datetime.now()
        seconds = now.hour * 60 * 60 + now.minute * 60 + now.second + now.microsecond / 1_000_000
        return now.year, now.month, now.day, seconds

    def _set_source(self, source: str):
        """
        Load shader templates, injects main function,
        create program and configures the program.
        """
        vs_path = arcade.resources.resolve(":system:shaders/shadertoy/base_vs.glsl")
        fs_path = arcade.resources.resolve(":system:shaders/shadertoy/base_fs.glsl")
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

    Args:
        size:
            Size of framebuffer / texture
        source:
            mainImage shader source
        repeat:
            Repeat/wrap mode for the underlying texture
    """

    def __init__(self, size: tuple[int, int], source: str, repeat: bool = False):
        super().__init__(size, source)
        self._texture = self.ctx.texture(self._size, components=4)
        self._fbo = self.ctx.framebuffer(color_attachments=[self._texture])
        self._repeat = repeat
        self._set_repeat()

    @property
    def texture(self) -> Texture2D:
        """
        The OpenGL texture for this buffer.
        This can be assigned to channels.
        """
        return self._texture

    @property
    def fbo(self) -> Framebuffer:
        """The framebuffer for this buffer"""
        return self._fbo

    @property
    def repeat(self) -> bool:
        """
        Get or set texture repeat.
        """
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

    def resize(self, size: tuple[int, int]):
        """
        Change the internal buffer size.

        Args:
            size: New size
        """
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

    Args:
        size: pixel size if the output
        main_source: The main glsl source with mainImage function
    """

    def __init__(self, size: tuple[int, int], main_source: str):
        super().__init__(size, main_source)

        self._buffer_a: ShadertoyBuffer | None = None
        self._buffer_b: ShadertoyBuffer | None = None
        self._buffer_c: ShadertoyBuffer | None = None
        self._buffer_d: ShadertoyBuffer | None = None

    @property
    def buffer_a(self) -> ShadertoyBuffer | None:
        """Get or set buffer a"""
        return self._buffer_a

    @buffer_a.setter
    def buffer_a(self, value):
        self._buffer_a = value

    @property
    def buffer_b(self) -> ShadertoyBuffer | None:
        """Get or set buffer b"""
        return self._buffer_b

    @buffer_b.setter
    def buffer_b(self, value):
        self._buffer_b = value

    @property
    def buffer_c(self) -> ShadertoyBuffer | None:
        """Get or set buffer c"""
        return self._buffer_c

    @buffer_c.setter
    def buffer_c(self, value):
        self._buffer_c = value

    @property
    def buffer_d(self) -> ShadertoyBuffer | None:
        """Get or set buffer d"""
        return self._buffer_d

    @buffer_d.setter
    def buffer_d(self, value):
        self._buffer_d = value

    @classmethod
    def create_from_file(cls, size: tuple[int, int], path: str | Path) -> "Shadertoy":
        """
        Create a Shadertoy from a mainImage shader file.

        Args:
            size: Size of shadertoy in pixels
            path: Path to mainImage shader file
        """
        path = arcade.resources.resolve(path)
        with open(path) as fd:
            source = fd.read()
        return cls(size, source)

    def create_buffer(self, source: str, repeat: bool = False) -> ShadertoyBuffer:
        """
        Shortcut for creating a buffer from mainImage shader file.

        Args:
            source: Path to shader file
            repeat: Buffer/texture repeat at borders
        """
        return ShadertoyBuffer(self._size, source, repeat=repeat)

    def create_buffer_from_file(self, path: str | Path) -> ShadertoyBuffer:
        """
        Shortcut for creating a ShadertoyBuffer from shaders source.
        The size of the framebuffer will be the same as the Shadertoy.

        Args:
            path: Path to shader source
        """
        path = arcade.resources.resolve(path)
        with open(path) as fd:
            source = fd.read()
        return ShadertoyBuffer(self._size, source)

    def resize(self, size: tuple[int, int]):
        """
        Resize the internal buffers

        Args:
            size: The new size in pixels
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
