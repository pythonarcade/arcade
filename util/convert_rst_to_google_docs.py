"""
Attempt to convert the docstrings in the Arcade codebase from RST to Google Docs format.

https://github.com/pythonarcade/arcade/issues/1797
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import typer
from typing_extensions import Annotated

fn_signature_w_docstring_regexp = re.compile(
    r"""
    (?P<fn_signature>
        (?P<fn_signature_before>
            def \s+
            (?P<fn_name> \S+ )              # Function name
            \( .*? \)                       # Parameter list
        )
        (?P<rtype_anno>                     # Return type annotation
            \s* -> \s*
            (?P<rtype_anno_type> .{1,300}? )
        )?
        :
    )
    [\r?\n\s]+
    (?P<docstring>
        \"\"\"                      # Docstring start
        (?P<docstring_body> .*? )
        \"\"\"                          # Docstring end
    )
    """,
    re.X | re.DOTALL)

docstring_rtype_regexp = re.compile(
    r"""
        \ +
        :rtype: \s* (?P<rtype> .*? ) \r?\n
    """,
    re.X | re.DOTALL)

app = typer.Typer()


@dataclass
class ReplacementContext:
    num_files_updated: int = 0
    num_rtypes_removed: int = 0
    fix: bool = False

    def process_file(self, path: str | Path) -> None:
        resolved = Path(path).expanduser().resolve()
        content = resolved.read_text()
        edited = False

        file_position = 0  # Index in file

        while True:
            match = fn_signature_w_docstring_regexp.search(content, pos=file_position)
            if match:
                offset = 0
                rtype_match = docstring_rtype_regexp.search(match.group('docstring'))
                if rtype_match:
                    # print(match.groupdict() | rtype_match.groupdict())
                    # print(match.group('fn_signature') + match.group('docstring'))
                    if rtype_match:
                        # Remove rtype annotation from docstring
                        range = match.start('docstring') + rtype_match.start(), match.start('docstring') + rtype_match.end()
                        offset -= range[1] - range[0]
                        # TODO: optimize if needed
                        content = content[:range[0]] + content[range[1]:]
                        edited = True
                    if rtype_match and not match.group('rtype_anno'):
                        print(str(resolved), ":", match.group('fn_name'))
                        insert = f" -> {rtype_match.group('rtype')}"
                        file_position = match.end('fn_signature_before')
                        content = content[:file_position] + insert + content[file_position:]
                        offset += len(insert)

                    self.num_rtypes_removed += 1
                file_position = match.end() + offset
            else:
                break
        if self.fix:
            resolved.write_text(content)
        self.num_files_updated += int(edited)


@app.command()
def main(
        paths: Annotated[list[Path], typer.Argument(help='A file or files to process.')],
        fix: Annotated[bool, typer.Option(help="Whether to apply fixes or merely check.")] = False
):
    context = ReplacementContext(fix=fix)
    for path in paths:
       context.process_file(path)

    if fix:
        prefix = "Wrote"
    else:
        prefix = "Detected"

    print(f"{prefix} {context.num_files_updated=}")
    print(f"{prefix} {context.num_rtypes_removed=}")


if __name__ == "__main__":
    app()
