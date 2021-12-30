from typing import Dict, List
import re

from pyglet import gl

from .exceptions import ShaderException
from .types import SHADER_TYPE_NAMES


class ShaderSource:
    """
    GLSL source container for making source parsing simpler.
    We support locating out attributes and applying #defines values.

    This wrapper should ideally contain an unmodified version
    of the original source for caching. Getting the specific
    source with defines applied through ``get_source``.

    NOTE: We do assume the source is neat enough to be parsed
    this way and don't contain several statements on one line.

    :param Context ctx: The context this framebuffer belongs to
    :param List[arcade.gl.Texture] color_attachments: List of color attachments.
    :param arcade.gl.Texture depth_attachment: A depth attachment (optional)
    """

    def __init__(self, source: str, source_type: gl.GLenum):
        """Create a shader source wrapper."""
        self._source = source.strip()
        self._type = source_type
        self._lines = self._source.split("\n") if source else []
        self._out_attributes = []  # type: List[str]

        if not self._lines:
            raise ValueError("Shader source is empty")

        self._version = self._find_glsl_version()

        if self._type in [gl.GL_VERTEX_SHADER, gl.GL_GEOMETRY_SHADER]:
            self._parse_out_attributes()

    @property
    def version(self) -> int:
        """The glsl version"""
        return self._version

    @property
    def out_attributes(self) -> List[str]:
        """The out attributes for this program"""
        return self._out_attributes

    def get_source(self, *, defines: Dict[str, str] = None) -> str:
        """Return the shader source

        :param dict defines: Defines to replace in the source.
        """
        if not defines:
            return self._source

        lines = ShaderSource.apply_defines(self._lines, defines)
        return "\n".join(lines)

    def _find_glsl_version(self) -> int:
        if self._lines[0].strip().startswith("#version"):
            try:
                return int(self._lines[0].split()[1])
            except Exception:
                pass

        source = "\n".join(
            f"{str(i+1).zfill(3)}: {line} " for i, line in enumerate(self._lines)
        )

        raise ShaderException(
            (
                "Cannot find #version in shader source. "
                "Please provide at least a #version 330 statement in the beginning of the shader.\n"
                f"---- [{SHADER_TYPE_NAMES[self._type]}] ---\n"
                f"{source}"
            )
        )

    @staticmethod
    def apply_defines(lines: List[str], defines: Dict[str, str]) -> List[str]:
        """Locate and apply #define values

        :param List[str] lines: List of source lines
        :param dict defines: dict with ``name: value`` pairs.
        """
        for nr, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#define"):
                try:
                    name = line.split()[1]
                    value = defines.get(name)
                    if not value:
                        continue

                    lines[nr] = "#define {} {}".format(name, str(value))
                except IndexError:
                    pass

        return lines

    def _parse_out_attributes(self):
        """Locates out attributes so we don't have to manually supply them"""
        for line in self._lines:
            res = re.match(
                r"(layout(.+)\))?(\s+)?(out)(\s+)(\w+)(\s+)(\w+)", line.strip()
            )
            if res:
                self._out_attributes.append(res.groups()[-1])
