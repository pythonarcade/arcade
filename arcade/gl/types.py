import re
from typing import Iterable, Sequence, TypeAlias, Union

from arcade.types import BufferProtocol

from . import enums
from .buffer import Buffer

BufferOrBufferProtocol = Union[BufferProtocol, Buffer]

GLenumLike = int
PyGLenum = int
GLuintLike = int
PyGLuint = int


OpenGlFilter: TypeAlias = tuple[PyGLenum, PyGLenum]
BlendFunction: TypeAlias = Union[
    tuple[PyGLenum, PyGLenum], tuple[PyGLenum, PyGLenum, PyGLenum, PyGLenum]
]

#: Depth compare functions
compare_funcs: dict[str | None, int] = {
    None: enums.NONE,
    "<=": enums.LEQUAL,
    "<": enums.LESS,
    ">=": enums.GEQUAL,
    ">": enums.GREATER,
    "==": enums.EQUAL,
    "!=": enums.NOTEQUAL,
    "0": enums.NEVER,
    "1": enums.ALWAYS,
}

_float_base_format = (0, enums.RED, enums.RG, enums.RGB, enums.RGBA)
_int_base_format = (
    0,
    enums.RED_INTEGER,
    enums.RG_INTEGER,
    enums.RGB_INTEGER,
    enums.RGBA_INTEGER,
)
#: Pixel format lookup (base_format, internal_format, type, size)
pixel_formats = {
    # float formats
    "f1": (
        _float_base_format,
        (0, enums.R8, enums.RG8, enums.RGB8, enums.RGBA8),
        enums.UNSIGNED_BYTE,
        1,
    ),
    "f2": (
        _float_base_format,
        (0, enums.R16F, enums.RG16F, enums.RGB16F, enums.RGBA16F),
        enums.HALF_FLOAT,
        2,
    ),
    "f4": (
        _float_base_format,
        (0, enums.R32F, enums.RG32F, enums.RGB32F, enums.RGBA32F),
        enums.FLOAT,
        4,
    ),
    # int formats
    "i1": (
        _int_base_format,
        (0, enums.R8I, enums.RG8I, enums.RGB8I, enums.RGBA8I),
        enums.BYTE,
        1,
    ),
    "i2": (
        _int_base_format,
        (0, enums.R16I, enums.RG16I, enums.RGB16I, enums.RGBA16I),
        enums.SHORT,
        2,
    ),
    "i4": (
        _int_base_format,
        (0, enums.R32I, enums.RG32I, enums.RGB32I, enums.RGBA32I),
        enums.INT,
        4,
    ),
    # uint formats
    "u1": (
        _int_base_format,
        (0, enums.R8UI, enums.RG8UI, enums.RGB8UI, enums.RGBA8UI),
        enums.UNSIGNED_BYTE,
        1,
    ),
    "u2": (
        _int_base_format,
        (0, enums.R16UI, enums.RG16UI, enums.RGB16UI, enums.RGBA16UI),
        enums.UNSIGNED_SHORT,
        2,
    ),
    "u4": (
        _int_base_format,
        (0, enums.R32UI, enums.RG32UI, enums.RGB32UI, enums.RGBA32UI),
        enums.UNSIGNED_INT,
        4,
    ),
}


#: String representation of a shader types
SHADER_TYPE_NAMES = {
    enums.VERTEX_SHADER: "vertex shader",
    enums.FRAGMENT_SHADER: "fragment shader",
    enums.GEOMETRY_SHADER: "geometry shader",  # Not supported in WebGL
    enums.TESS_CONTROL_SHADER: "tessellation control shader",  # Not supported in WebGL
    enums.TESS_EVALUATION_SHADER: "tessellation evaluation shader",  # Not supported in WebGL
}

#: Lookup table for OpenGL type names
GL_NAMES = {
    enums.HALF_FLOAT: "GL_HALF_FLOAT",
    enums.FLOAT: "GL_FLOAT",
    enums.DOUBLE: "GL_DOUBLE",  # Double not supported in WebGL
    enums.INT: "GL_INT",
    enums.UNSIGNED_INT: "GL_UNSIGNED_INT",
    enums.SHORT: "GL_SHORT",
    enums.UNSIGNED_SHORT: "GL_UNSIGNED_SHORT",
    enums.BYTE: "GL_BYTE",
    enums.UNSIGNED_BYTE: "GL_UNSIGNED_BYTE",
}


def gl_name(gl_type):
    """Return the name of a gl type"""
    if gl_type is None:
        return None
    return GL_NAMES.get(gl_type, gl_type)


class AttribFormat:
    """
    Represents a vertex attribute in a BufferDescription / Program.
    This is attribute metadata used when attempting to map vertex
    shader inputs.

    Args:
        name:
            Name of the attribute
        gl_type:
            The OpenGL type such as GL_FLOAT, GL_HALF_FLOAT etc.
        bytes_per_component:
            Number of bytes for a single component
        offset:
            Offset for BufferDescription
        location:
            Location for program attribute
    """

    __slots__ = (
        "name",
        "gl_type",
        "components",
        "bytes_per_component",
        "offset",
        "location",
    )

    def __init__(
        self,
        name: str | None,
        gl_type,
        components: int,
        bytes_per_component: int,
        offset=0,
        location=0,
    ):
        self.name = name
        """The name of the attribute in the program"""
        self.gl_type = gl_type
        """The OpenGL type of the attribute"""
        self.components = components
        """Number of components for this attribute (1, 2, 3 or 4)"""
        self.bytes_per_component = bytes_per_component
        """How many bytes for a single component"""
        self.offset = offset
        """Offset of the attribute in the buffer"""
        self.location = location
        """Location of the attribute in the program"""

    @property
    def bytes_total(self) -> int:
        """Total number of bytes for this attribute"""
        return self.components * self.bytes_per_component

    def __repr__(self):
        return (
            f"<AttribFormat {self.name} {self.gl_type} components={self.components} "
            f"bytes_per_component={self.bytes_per_component}>"
        )


class BufferDescription:
    """Buffer Object description used with :py:class:`arcade.gl.Geometry`.

    This class provides a Buffer object with a description of its content, allowing the
    a :py:class:`~arcade.gl.Geometry` object to correctly map shader attributes
    to a program/shader.

    The formats is a string providing the number and type of each attribute. Currently
    we only support f (float), i (integer) and B (unsigned byte).

    ``normalized`` enumerates the attributes which must have their values normalized.
    This is useful for instance for colors attributes given as unsigned byte and
    normalized to floats with values between 0.0 and 1.0.

    ``instanced`` allows this buffer to be used as instanced buffer. Each value will
    be used once for the whole geometry. The geometry will be repeated a number of
    times equal to the number of items in the Buffer.

    .. code-block:: python

        # Describe my_buffer
        # It contains two floating point numbers being a 2d position
        # and two floating point numbers being texture coordinates.
        # We expect the shader using this buffer to have an in_pos and in_uv attribute (exact name)
        BufferDescription(
            my_buffer,
            '2f 2f',
            ['in_pos', 'in_uv'],
        )

    Args:
        buffer: The buffer to describe
        formats: The format of each attribute
        attributes: List of attributes names (strings)
        normalized: list of attribute names that should be normalized
        instanced: ``True`` if this is per instance data
    """

    # Describe all variants of a format string to simplify parsing (single component)
    # format: gl_type, byte_size
    _formats: dict[str, tuple] = {
        # (gl enum, byte size)
        # Floats
        "f": (enums.FLOAT, 4),
        "f1": (enums.UNSIGNED_BYTE, 1),
        "f2": (enums.HALF_FLOAT, 2),
        "f4": (enums.FLOAT, 4),
        "f8": (enums.DOUBLE, 8),  # Double unsupported by WebGL
        # Unsigned integers
        "u": (enums.UNSIGNED_INT, 4),
        "u1": (enums.UNSIGNED_BYTE, 1),
        "u2": (enums.UNSIGNED_SHORT, 2),
        "u4": (enums.UNSIGNED_INT, 4),
        # Signed integers
        "i": (enums.INT, 4),
        "i1": (enums.BYTE, 1),
        "i2": (enums.SHORT, 2),
        "i4": (enums.INT, 4),
        # Padding (1, 2, 4, 8 bytes)
        "x": (None, 1),
        "x1": (None, 1),
        "x2": (None, 2),
        "x4": (None, 4),
        "x8": (None, 8),
    }

    __slots__ = (
        "buffer",
        "attributes",
        "normalized",
        "instanced",
        "formats",
        "stride",
        "num_vertices",
    )

    def __init__(
        self,
        buffer: Buffer,
        formats: str,
        attributes: Sequence[str],
        normalized: Iterable[str] | None = None,
        instanced: bool = False,
    ):
        #: The :py:class:`~arcade.gl.Buffer` this description object describes
        self.buffer = buffer  # type: Buffer
        #: List of string attributes
        self.attributes = attributes
        #: List of normalized attributes
        self.normalized: set[str] = set() if normalized is None else set(normalized)
        #: Instanced flag (bool)
        self.instanced: bool = instanced
        #: Formats of each attribute
        self.formats: list[AttribFormat] = []
        #: The byte stride of the buffer
        self.stride: int = -1
        #: Number of vertices in the buffer
        self.num_vertices: int = -1

        if not isinstance(buffer, Buffer):
            raise ValueError("buffer parameter must be an arcade.gl.Buffer")

        if not isinstance(self.attributes, (list, tuple)):
            raise ValueError("Attributes must be a list or tuple")

        if self.normalized > set(self.attributes):
            raise ValueError("Normalized attribute not found in attributes.")

        formats_list = formats.split(" ")
        non_padded_formats = [f for f in formats_list if "x" not in f]

        if len(non_padded_formats) != len(self.attributes):
            raise ValueError(
                f"Different lengths of formats ({len(non_padded_formats)}) and "
                f"attributes ({len(self.attributes)})"
            )

        def zip_attrs(formats: list[str], attributes: Sequence[str]):
            """Join together formats and attribute names taking padding into account"""
            attr_index = 0
            for f in formats:
                if "x" in f:
                    yield f, None
                else:
                    yield f, attributes[attr_index]
                    attr_index += 1

        self.stride = 0
        for attr_fmt, attr_name in zip_attrs(formats_list, self.attributes):
            # Automatically make f1 attributes normalized
            if attr_name is not None and "f1" in attr_fmt:
                self.normalized.add(attr_name)
            try:
                components_str, data_type_str, data_size_str = re.split(r"([fiux])", attr_fmt)
                data_type = f"{data_type_str}{data_size_str}" if data_size_str else data_type_str
                components = int(components_str) if components_str else 1  # 1 component is default
                data_size = (
                    int(data_size_str) if data_size_str else 4
                )  # 4 byte float and integer types are default
                # Limit components to 4 for non-padded formats
                if components > 4 and data_size is not None:
                    raise ValueError("Number of components must be 1, 2, 3 or 4")
            except Exception as ex:
                raise ValueError(f"Could not parse attribute format: '{attr_fmt} : {ex}'")

            gl_type, byte_size = self._formats[data_type]
            self.formats.append(
                AttribFormat(attr_name, gl_type, components, byte_size, offset=self.stride)
            )

            self.stride += byte_size * components

        if self.buffer.size % self.stride != 0:
            raise ValueError(
                f"Buffer size must align by {self.stride} bytes. "
                f"{self.buffer} size={self.buffer.size}"
            )

        # Estimate number of vertices for this buffer
        self.num_vertices = self.buffer.size // self.stride

    def __repr__(self) -> str:
        return f"<BufferDescription {self.attributes} {self.formats}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, BufferDescription):
            raise ValueError(
                f"The only logical comparison to a BufferDescription"
                f"is a BufferDescription not {type(other)}"
            )

        # Equal if we share the same attribute
        return len(set(self.attributes) & set(other.attributes)) > 0


class TypeInfo:
    """
    Describes an opengl type.

    Args:
        name:
            The string representation of this type
        enum:
            The enum of this type
        gl_type:
            The base enum of this type
        gl_size:
            byte size if the gl_type
        components:
            Number of components for this enum
    """

    __slots__ = "name", "enum", "gl_type", "gl_size", "components"

    def __init__(self, name: str, enum, gl_type, gl_size: int, components: int):
        self.name = name
        """The string representation of this type"""
        self.enum = enum
        """The OpenEL enum of this type"""
        self.gl_type = gl_type
        """The base OpenGL data type"""
        self.gl_size = gl_size
        """The size of the base OpenGL data type"""
        self.components = components
        """The number of components (1, 2, 3 or 4)"""

    @property
    def size(self) -> int:
        """The total size of this type in bytes"""
        return self.gl_size * self.components

    def __repr__(self) -> str:
        return (
            f"<TypeInfo name={self.name}, enum={self.enum} gl_type={self.gl_type} "
            f"gl_size={self.gl_size} components={self.components}>"
        )


class GLTypes:
    """
    Detailed Information about all attribute type.

    During introspection we often just get integers telling us what type is used.
    This can for example be ``35664`` telling us it's a ``GL_FLOAT_VEC2``.

    During introspection we need to know the exact datatype of the attribute.
    It's not enough to know it's a float, we need to know if it's a vec2, vec3, vec4
    or any other type that OpenGL supports.

    Examples of types are::

        GL_FLOAT_VEC2
        GL_DOUBLE_VEC4
        GL_INT_VEC3
        GL_UNSIGNED_INT_VEC2
        GL_UNSIGNED_BYTE
        GL_FLOAT
        GL_DOUBLE
        GL_INT
        GL_UNSIGNED_INT
        ...
    """

    types = {
        # Floats
        enums.FLOAT: TypeInfo("GL_FLOAT", enums.FLOAT, enums.FLOAT, 4, 1),
        enums.FLOAT_VEC2: TypeInfo("GL_FLOAT_VEC2", enums.FLOAT_VEC2, enums.FLOAT, 4, 2),
        enums.FLOAT_VEC3: TypeInfo("GL_FLOAT_VEC3", enums.FLOAT_VEC3, enums.FLOAT, 4, 3),
        enums.FLOAT_VEC4: TypeInfo("GL_FLOAT_VEC4", enums.FLOAT_VEC4, enums.FLOAT, 4, 4),
        # Doubles -- Unsupported by WebGL
        enums.DOUBLE: TypeInfo("GL_DOUBLE", enums.DOUBLE, enums.DOUBLE, 8, 1),
        enums.DOUBLE_VEC2: TypeInfo("GL_DOUBLE_VEC2", enums.DOUBLE_VEC2, enums.DOUBLE, 8, 2),
        enums.DOUBLE_VEC3: TypeInfo("GL_DOUBLE_VEC3", enums.DOUBLE_VEC3, enums.DOUBLE, 8, 3),
        enums.DOUBLE_VEC4: TypeInfo("GL_DOUBLE_VEC4", enums.DOUBLE_VEC4, enums.DOUBLE, 8, 4),
        # Booleans (ubyte)
        enums.BOOL: TypeInfo("GL_BOOL", enums.BOOL, enums.BOOL, 1, 1),
        enums.BOOL_VEC2: TypeInfo("GL_BOOL_VEC2", enums.BOOL_VEC2, enums.BOOL, 1, 2),
        enums.BOOL_VEC3: TypeInfo("GL_BOOL_VEC3", enums.BOOL_VEC3, enums.BOOL, 1, 3),
        enums.BOOL_VEC4: TypeInfo("GL_BOOL_VEC4", enums.BOOL_VEC4, enums.BOOL, 1, 4),
        # Integers
        enums.INT: TypeInfo("GL_INT", enums.INT, enums.INT, 4, 1),
        enums.INT_VEC2: TypeInfo("GL_INT_VEC2", enums.INT_VEC2, enums.INT, 4, 2),
        enums.INT_VEC3: TypeInfo("GL_INT_VEC3", enums.INT_VEC3, enums.INT, 4, 3),
        enums.INT_VEC4: TypeInfo("GL_INT_VEC4", enums.INT_VEC4, enums.INT, 4, 4),
        # Unsigned Integers
        enums.UNSIGNED_INT: TypeInfo(
            "GL_UNSIGNED_INT", enums.UNSIGNED_INT, enums.UNSIGNED_INT, 4, 1
        ),
        enums.UNSIGNED_INT_VEC2: TypeInfo(
            "GL_UNSIGNED_INT_VEC2", enums.UNSIGNED_INT_VEC2, enums.UNSIGNED_INT, 4, 2
        ),
        enums.UNSIGNED_INT_VEC3: TypeInfo(
            "GL_UNSIGNED_INT_VEC3", enums.UNSIGNED_INT_VEC3, enums.UNSIGNED_INT, 4, 3
        ),
        enums.UNSIGNED_INT_VEC4: TypeInfo(
            "GL_UNSIGNED_INT_VEC4", enums.UNSIGNED_INT_VEC4, enums.UNSIGNED_INT, 4, 4
        ),
        # Unsigned Short (mostly used for short index buffers)
        enums.UNSIGNED_SHORT: TypeInfo(
            "GL.GL_UNSIGNED_SHORT", enums.UNSIGNED_SHORT, enums.UNSIGNED_SHORT, 2, 2
        ),
        # Byte
        enums.BYTE: TypeInfo("GL_BYTE", enums.BYTE, enums.BYTE, 1, 1),
        enums.UNSIGNED_BYTE: TypeInfo(
            "GL_UNSIGNED_BYTE", enums.UNSIGNED_BYTE, enums.UNSIGNED_BYTE, 1, 1
        ),
        # Matrices
        enums.FLOAT_MAT2: TypeInfo("GL_FLOAT_MAT2", enums.FLOAT_MAT2, enums.FLOAT, 4, 4),
        enums.FLOAT_MAT3: TypeInfo("GL_FLOAT_MAT3", enums.FLOAT_MAT3, enums.FLOAT, 4, 9),
        enums.FLOAT_MAT4: TypeInfo("GL_FLOAT_MAT4", enums.FLOAT_MAT4, enums.FLOAT, 4, 16),
        enums.FLOAT_MAT2x3: TypeInfo("GL_FLOAT_MAT2x3", enums.FLOAT_MAT2x3, enums.FLOAT, 4, 6),
        enums.FLOAT_MAT2x4: TypeInfo("GL_FLOAT_MAT2x4", enums.FLOAT_MAT2x4, enums.FLOAT, 4, 8),
        enums.FLOAT_MAT3x2: TypeInfo("GL_FLOAT_MAT3x2", enums.FLOAT_MAT3x2, enums.FLOAT, 4, 6),
        enums.FLOAT_MAT3x4: TypeInfo("GL_FLOAT_MAT3x4", enums.FLOAT_MAT3x4, enums.FLOAT, 4, 12),
        enums.FLOAT_MAT4x2: TypeInfo("GL_FLOAT_MAT4x2", enums.FLOAT_MAT4x2, enums.FLOAT, 4, 8),
        enums.FLOAT_MAT4x3: TypeInfo("GL_FLOAT_MAT4x3", enums.FLOAT_MAT4x3, enums.FLOAT, 4, 12),
        # Double matrices -- unsupported by WebGL
        enums.DOUBLE_MAT2: TypeInfo("GL_DOUBLE_MAT2", enums.DOUBLE_MAT2, enums.DOUBLE, 8, 4),
        enums.DOUBLE_MAT3: TypeInfo("GL_DOUBLE_MAT3", enums.DOUBLE_MAT3, enums.DOUBLE, 8, 9),
        enums.DOUBLE_MAT4: TypeInfo("GL_DOUBLE_MAT4", enums.DOUBLE_MAT4, enums.DOUBLE, 8, 16),
        enums.DOUBLE_MAT2x3: TypeInfo("GL_DOUBLE_MAT2x3", enums.DOUBLE_MAT2x3, enums.DOUBLE, 8, 6),
        enums.DOUBLE_MAT2x4: TypeInfo("GL_DOUBLE_MAT2x4", enums.DOUBLE_MAT2x4, enums.DOUBLE, 8, 8),
        enums.DOUBLE_MAT3x2: TypeInfo("GL_DOUBLE_MAT3x2", enums.DOUBLE_MAT3x2, enums.DOUBLE, 8, 6),
        enums.DOUBLE_MAT3x4: TypeInfo("GL_DOUBLE_MAT3x4", enums.DOUBLE_MAT3x4, enums.DOUBLE, 8, 12),
        enums.DOUBLE_MAT4x2: TypeInfo("GL_DOUBLE_MAT4x2", enums.DOUBLE_MAT4x2, enums.DOUBLE, 8, 8),
        enums.DOUBLE_MAT4x3: TypeInfo("GL_DOUBLE_MAT4x3", enums.DOUBLE_MAT4x3, enums.DOUBLE, 8, 12),
        # TODO: Add sampler types if needed. Only needed for better uniform introspection.
    }

    @classmethod
    def get(cls, enum: int) -> TypeInfo:
        """Get the TypeInfo for a given"""
        try:
            return cls.types[enum]
        except KeyError:
            raise ValueError(f"Unknown gl type {enum}. Someone needs to add it")
