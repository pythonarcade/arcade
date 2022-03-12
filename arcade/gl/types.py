import re
from typing import Iterable, List

from pyglet import gl

from .buffer import Buffer


_float_base_format = (0, gl.GL_RED, gl.GL_RG, gl.GL_RGB, gl.GL_RGBA)
_int_base_format = (
    0,
    gl.GL_RED_INTEGER,
    gl.GL_RG_INTEGER,
    gl.GL_RGB_INTEGER,
    gl.GL_RGBA_INTEGER,
)
# format: (base_format, internal_format, type, size)
pixel_formats = {
    # float formats
    "f1": (
        _float_base_format,
        (0, gl.GL_R8, gl.GL_RG8, gl.GL_RGB8, gl.GL_RGBA8),
        gl.GL_UNSIGNED_BYTE,
        1,
    ),
    "f2": (
        _float_base_format,
        (0, gl.GL_R16F, gl.GL_RG16F, gl.GL_RGB16F, gl.GL_RGBA16F),
        gl.GL_HALF_FLOAT,
        2,
    ),
    "f4": (
        _float_base_format,
        (0, gl.GL_R32F, gl.GL_RG32F, gl.GL_RGB32F, gl.GL_RGBA32F),
        gl.GL_FLOAT,
        4,
    ),
    # int formats
    "i1": (
        _int_base_format,
        (0, gl.GL_R8I, gl.GL_RG8I, gl.GL_RGB8I, gl.GL_RGBA8I),
        gl.GL_BYTE,
        1,
    ),
    "i2": (
        _int_base_format,
        (0, gl.GL_R16I, gl.GL_RG16I, gl.GL_RGB16I, gl.GL_RGBA16I),
        gl.GL_SHORT,
        2,
    ),
    "i4": (
        _int_base_format,
        (0, gl.GL_R32I, gl.GL_RG32I, gl.GL_RGB32I, gl.GL_RGBA32I),
        gl.GL_INT,
        4,
    ),
    # uint formats
    "u1": (
        _int_base_format,
        (0, gl.GL_R8UI, gl.GL_RG8UI, gl.GL_RGB8UI, gl.GL_RGBA8UI),
        gl.GL_UNSIGNED_BYTE,
        1,
    ),
    "u2": (
        _int_base_format,
        (0, gl.GL_R16UI, gl.GL_RG16UI, gl.GL_RGB16UI, gl.GL_RGBA16UI),
        gl.GL_UNSIGNED_SHORT,
        2,
    ),
    "u4": (
        _int_base_format,
        (0, gl.GL_R32UI, gl.GL_RG32UI, gl.GL_RGB32UI, gl.GL_RGBA32UI),
        gl.GL_UNSIGNED_INT,
        4,
    ),
}


# String representation of a shader type
SHADER_TYPE_NAMES = {
    gl.GL_VERTEX_SHADER: "vertex shader",
    gl.GL_FRAGMENT_SHADER: "fragment shader",
    gl.GL_GEOMETRY_SHADER: "geometry shader",
    gl.GL_TESS_CONTROL_SHADER: "tessellation control shader",
    gl.GL_TESS_EVALUATION_SHADER: "tessellation evaluation shader",
}


class AttribFormat:
    """"
    Represents an attribute in a BufferDescription or a Program.

    :param str name: Name of the attribute
    :param gl.GLEnum gl_type: The OpenGL type such as GL_FLOAT, GL_HALF_FLOAT etc.
    :param int bytes_per_component: Number of bytes a single component takes
    :param int offset: (Optional offset for BufferDescription)
    :param int location: (Optional location for program attribute)
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
        self, name, gl_type, components, bytes_per_component, offset=0, location=0
    ):
        self.name = name  # type: str
        self.gl_type = gl_type  # type: gl.GLenum
        self.components = components  # type: int
        self.bytes_per_component = bytes_per_component  # type: int
        self.offset = offset  # type: int
        self.location = location  # type: int

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

    Example::

        # Describe my_buffer
        # It contains two floating point numbers being a 2d position
        # and two floating point numbers being texture coordinates.
        # We expect the shader using this buffer to have an in_pos and in_uv attribute (exact name)
        BufferDescription(
            my_buffer,
            '2f 2f',
            ['in_pos', 'in_uv'],
        )

    :param Buffer buffer: The buffer to describe
    :param str formats: The format of each attribute
    :param list attributes: List of attributes names (strings)
    :param list normalized: list of attribute names that should be normalized
    :param bool instanced: ``True`` if this is per instance data
    """

    # Describe all variants of a format string to simplify parsing (single component)
    # format: gl_type, byte_size
    _formats = {
        # (gl enum, byte size)
        # Floats
        "f": (gl.GL_FLOAT, 4),
        "f1": (gl.GL_UNSIGNED_BYTE, 1),
        "f2": (gl.GL_HALF_FLOAT, 2),
        "f4": (gl.GL_FLOAT, 4),
        "f8": (gl.GL_DOUBLE, 8),
        # Unsigned integers
        "u": (gl.GL_FLOAT, 4),
        "u1": (gl.GL_FLOAT, 1),
        "u2": (gl.GL_FLOAT, 2),
        "u4": (gl.GL_FLOAT, 4),
        # Signed integers
        "i": (gl.GL_INT, 4),
        "i1": (gl.GL_BYTE, 1),
        "i2": (gl.GL_SHORT, 2),
        "i4": (gl.GL_INT, 4),
        # Padding (1, 2, 4, 8 bytes)
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
        attributes: Iterable[str],
        normalized: Iterable[str] = None,
        instanced: bool = False,
    ):

        #: The :py:class:`~arcade.gl.Buffer` this description object describes
        self.buffer = buffer  # type: Buffer
        #: List of string attributes
        self.attributes = attributes
        #: List of normalized attributes
        self.normalized = set() if normalized is None else set(normalized)
        #: Instanced flag (bool)
        self.instanced = instanced  # type: bool
        #: Formats of each attribute
        self.formats = []  # type: List[AttribFormat]
        #: The byte stride of the buffer
        self.stride = -1  # type: int
        #: Number of vertices in the buffer
        self.num_vertices = -1  # type: int

        if not isinstance(buffer, Buffer):
            raise ValueError("buffer parameter must be an arcade.gl.Buffer")

        if not isinstance(self.attributes, list) and not isinstance(
            self.attributes, tuple
        ):
            raise ValueError("Attributes must be a list or tuple")

        if self.normalized > set(self.attributes):
            raise ValueError("Normalized attribute not found in attributes.")

        formats_list = formats.split(" ")
        non_padded_formats = [f for f in formats_list if "x" not in f]

        if len(non_padded_formats) != len(self.attributes):
            raise ValueError(
                f"Different lengths of formats ({len(formats_list)}) and "
                f"attributes ({len(self.attributes)})"
            )

        def zip_attrs(formats, attributes):
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
            try:
                components_str, data_type_str, data_size_str = re.split(
                    r"([fiux])", attr_fmt
                )
                data_type = (
                    f"{data_type_str}{data_size_str}"
                    if data_size_str
                    else data_type_str
                )
                components = (
                    int(components_str) if components_str else 1
                )  # 1 component is default
                data_size = (
                    int(data_size_str) if data_size_str else 4
                )  # 4 byte float and integer types are default
                # Limit components to 4 for non-padded formats
                if components > 4 and data_size is not None:
                    raise ValueError("Number of components must be 1, 2, 3 or 4")
            except Exception as ex:
                raise ValueError(
                    f"Could not parse attribute format: '{attr_fmt} : {ex}'"
                )

            gl_type, byte_size = self._formats[data_type]
            self.formats.append(
                AttribFormat(
                    attr_name, gl_type, components, byte_size, offset=self.stride
                )
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
        return f"<BufferDescription {self.formats}>"


class TypeInfo:
    """
    Describes an opengl type

    :param name: the string representation of this type
    :param enum: The enum of this type
    :param gl_type: the base enum of this type
    :param gl_size: byte size if the gl_type
    :param components: Number of components for this enum
    """
    __slots__ = "name", "enum", "gl_type", "gl_size", "components"

    def __init__(self, name, enum, gl_type, gl_size, components):

        self.name = name  # type: str
        self.enum = enum  # type: gl.GLenum
        self.gl_type = gl_type  # type: gl.GLenum
        self.gl_size = gl_size  # type: int
        self.components = components  # type: int

    @property
    def size(self) -> int:
        return self.gl_size * self.components

    def __repr__(self) -> str:
        return (
            f"<TypeInfo name={self.name}, enum={self.enum} gl_type={self.gl_type} "
            f"gl_size={self.gl_size} components={self.components}>"
        )


class GLTypes:
    """
    Get information about an attribute type.
    During introspection we often just get integers telling us what type is used.
    This can for example be `35664` telling us it's a `GL_FLOAT_VEC2`.
    We want to know this is a `gl.GLfloat` with 2 components so we can compare
    that to the types in the `BufferDescription`.
    These an also be used for uniform introspection.
    """
    types = {
        # Floats
        gl.GL_FLOAT: TypeInfo("GL_FLOAT", gl.GL_FLOAT, gl.GL_FLOAT, 4, 1),
        gl.GL_FLOAT_VEC2: TypeInfo(
            "GL_FLOAT_VEC2", gl.GL_FLOAT_VEC2, gl.GL_FLOAT, 4, 2
        ),
        gl.GL_FLOAT_VEC3: TypeInfo(
            "GL_FLOAT_VEC3", gl.GL_FLOAT_VEC3, gl.GL_FLOAT, 4, 3
        ),
        gl.GL_FLOAT_VEC4: TypeInfo(
            "GL_FLOAT_VEC4", gl.GL_FLOAT_VEC4, gl.GL_FLOAT, 4, 4
        ),
        # Doubles
        gl.GL_DOUBLE: TypeInfo("GL_DOUBLE", gl.GL_DOUBLE, gl.GL_DOUBLE, 8, 1),
        gl.GL_DOUBLE_VEC2: TypeInfo(
            "GL_DOUBLE_VEC2", gl.GL_DOUBLE_VEC2, gl.GL_DOUBLE, 8, 2
        ),
        gl.GL_DOUBLE_VEC3: TypeInfo(
            "GL_DOUBLE_VEC3", gl.GL_DOUBLE_VEC3, gl.GL_DOUBLE, 8, 3
        ),
        gl.GL_DOUBLE_VEC4: TypeInfo(
            "GL_DOUBLE_VEC4", gl.GL_DOUBLE_VEC4, gl.GL_DOUBLE, 8, 4
        ),
        # Booleans (ubyte)
        gl.GL_BOOL: TypeInfo("GL_BOOL", gl.GL_BOOL, gl.GL_BOOL, 1, 1),
        gl.GL_BOOL_VEC2: TypeInfo("GL_BOOL_VEC2", gl.GL_BOOL_VEC2, gl.GL_BOOL, 1, 2),
        gl.GL_BOOL_VEC3: TypeInfo("GL_BOOL_VEC3", gl.GL_BOOL_VEC3, gl.GL_BOOL, 1, 3),
        gl.GL_BOOL_VEC4: TypeInfo("GL_BOOL_VEC4", gl.GL_BOOL_VEC4, gl.GL_BOOL, 1, 4),
        # Integers
        gl.GL_INT: TypeInfo("GL_INT", gl.GL_INT, gl.GL_INT, 4, 1),
        gl.GL_INT_VEC2: TypeInfo("GL_INT_VEC2", gl.GL_INT_VEC2, gl.GL_INT, 4, 2),
        gl.GL_INT_VEC3: TypeInfo("GL_INT_VEC3", gl.GL_INT_VEC3, gl.GL_INT, 4, 3),
        gl.GL_INT_VEC4: TypeInfo("GL_INT_VEC4", gl.GL_INT_VEC4, gl.GL_INT, 4, 4),
        # Unsigned Integers
        gl.GL_UNSIGNED_INT: TypeInfo(
            "GL_UNSIGNED_INT", gl.GL_UNSIGNED_INT, gl.GL_UNSIGNED_INT, 4, 1
        ),
        gl.GL_UNSIGNED_INT_VEC2: TypeInfo(
            "GL_UNSIGNED_INT_VEC2", gl.GL_UNSIGNED_INT_VEC2, gl.GL_UNSIGNED_INT, 4, 2
        ),
        gl.GL_UNSIGNED_INT_VEC3: TypeInfo(
            "GL_UNSIGNED_INT_VEC3", gl.GL_UNSIGNED_INT_VEC3, gl.GL_UNSIGNED_INT, 4, 3
        ),
        gl.GL_UNSIGNED_INT_VEC4: TypeInfo(
            "GL_UNSIGNED_INT_VEC4", gl.GL_UNSIGNED_INT_VEC4, gl.GL_UNSIGNED_INT, 4, 4
        ),
        # Unsigned Short (mostly used for short index buffers)
        gl.GL_UNSIGNED_SHORT: TypeInfo(
            "GL.GL_UNSIGNED_SHORT", gl.GL_UNSIGNED_SHORT, gl.GL_UNSIGNED_SHORT, 2, 2
        ),
        # Byte
        gl.GL_BYTE: TypeInfo("GL_BYTE", gl.GL_BYTE, gl.GL_BYTE, 1, 1),
        gl.GL_UNSIGNED_BYTE: TypeInfo(
            "GL_UNSIGNED_BYTE", gl.GL_UNSIGNED_BYTE, gl.GL_UNSIGNED_BYTE, 1, 1
        ),
        # TODO: Add sampler types if needed. Only needed for better uniform introspection.
    }

    @classmethod
    def get(cls, enum: int):
        try:
            return cls.types[enum]
        except KeyError:
            raise ValueError(f"Unknown gl type {enum}. Someone needs to add it")
