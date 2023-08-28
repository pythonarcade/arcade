import glob
import re

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

count = 0
for file in [*glob.glob('arcade/*.py'), *glob.glob('arcade/**/*.py')]:
    with open(file, "r") as f:
        content = f.read()
    pos = 0
    while True:
        match = fn_signature_w_docstring_regexp.search(content, pos=pos)
        if match:
            offset = 0
            match2 = docstring_rtype_regexp.search(match.group('docstring'))
            if match2:
                # print(match.groupdict() | match2.groupdict())
                # print(match.group('fn_signature') + match.group('docstring'))
                count += 1
                if match2:
                    # Remove rtype annotation from docstring
                    range = match.start('docstring') + match2.start(), match.start('docstring') + match2.end()
                    offset -= range[1] - range[0]
                    content = content[:range[0]] + content[range[1]:]
                if match2 and not match.group('rtype_anno'):
                    print(file, match.group('fn_name'))
                    insert = f" -> {match2.group('rtype')}"
                    pos = match.end('fn_signature_before')
                    content = content[:pos] + insert + content[pos:]
                    offset += len(insert)

            pos = match.end() + offset
        else:
            break
    with open(file, "w") as f:
        f.write(content)
print(count)