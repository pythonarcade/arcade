from typing import Dict, Iterable, List, Optional
import re

from pyglet import gl

from .exceptions import ShaderException
from .types import SHADER_TYPE_NAMES


class ShaderSource:
    """
    GLSL source container for making source parsing simpler.
    We support locating out attributes, applying #defines values
    and injecting common source.

    This wrapper should ideally contain an unmodified version
    of the original source for caching. Getting the specific
    source with defines applied through ``get_source``.

    NOTE: We do assume the source is neat enough to be parsed
    this way and don't contain several statements on one line.

    :param Context ctx: The context this framebuffer belongs to
    :param str source: The source code
    :common List[str] common: Common source code to inject
    :param int source_type: The shader type
    :param arcade.gl.Texture depth_attachment: A depth attachment (optional)
    """
    def __init__(
        self,
        ctx: gl.Context,
        source: str,
        common: Optional[Iterable[str]],
        source_type: gl.GLenum,
    ):
        """Create a shader source wrapper."""
        self._source = source.strip()
        self._type = source_type
        self._lines = self._source.split("\n") if source else []
        self._out_attributes = []  # type: List[str]

        if not self._lines:
            raise ValueError("Shader source is empty")

        self._version = self._find_glsl_version()

        if ctx.gl_api == "gles":
            # TODO: Use the version from the context
            self._lines[0] = "#version 310 es"
            self._lines.insert(1, "precision mediump float;")

            if self._type == gl.GL_GEOMETRY_SHADER:
                self._lines.insert(1, "#extension GL_EXT_geometry_shader : require")

            if self._type == gl.GL_COMPUTE_SHADER:
                self._lines.insert(1, "precision mediump image2D;")

            self._version = self._find_glsl_version()

        # Inject common source
        self.inject_common_sources(common)

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

    def inject_common_sources(self, common: Optional[Iterable[str]]) -> None:
        """Inject common source code into the shader source"""
        if not common:
            return

        # Find the main function
        for line_number, line in enumerate(self._lines):
            if "main()" in line:
                break
        else:
            raise ShaderException("No main() function found when injecting common source")

        # Insert all common sources
        for source in common:
            lines = source.split("\n")
            self._lines = self._lines[:line_number] + lines + self._lines[line_number:]

    def get_source(self, *, defines: Optional[Dict[str, str]] = None) -> str:
        """Return the shader source

        :param dict defines: Defines to replace in the source.
        """
        if not defines:
            return "\n".join(self._lines)

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
