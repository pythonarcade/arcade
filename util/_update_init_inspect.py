import inspect
from importlib import import_module
import typing
from pathlib import Path
from string import Template

# IMPORTANT: 
import arcade

MODULE_PATH = Path(__file__).parent.resolve()
ARCADE_PATH = (MODULE_PATH / "../arcade").resolve()

# Names we want to exclude from arcade
EXCLUDE = [
    "LOG",
    "TYPE_CHECKING",
]

# Modules to include in __init__
# NODE: Possibly introspect these and make exclusion instead?
MODULES = (
    "window_commands",
    "application",
    "arcade_types",
    "earclip_module",
    "utils",
    "drawing_support",
    "texture",
    "buffered_draw_commands",
    "draw_commands",
    "geometry",
    "isometric",
    "joysticks",
    "emitter",
    "emitter_simple",
    "particle",
    "sound",
    "sprite",
    "sprite_list",
    "physics_engines",
    "text",
    "tilemap",
    "pymunk_physics_engine",
    "version",
    "paths",
    "context",
    "texture_atlas",
)


def main():
    with open(MODULE_PATH / 'template_init.py', 'r') as content_file:
        init_template = Template(content_file.read())

    import_strings = ""
    all_list = []

    for module_name in MODULES:
        inspector = ModuleInspector(module_name)

        for name, module in inspector.attributes:
            import_strings += f"from .{module} import {name}\n"
            all_list.append(name)
        for name, module in inspector.classes:
            import_strings += f"from .{module} import {name}\n"
            all_list.append(name)
        for name, module in inspector.functions:
            import_strings += f"from .{module} import {name}\n"
            all_list.append(name)

        import_strings += "\n"

    all_list.sort()
    all_strings = "\n__all__ = [\n"
    for entry in all_list:
        all_strings += f"    '{entry}',\n"
    all_strings += "]\n\n"
    all_strings += "__version__ = VERSION\n"

    text_file = open(ARCADE_PATH / "__init__.py", "w")
    text_file.write(init_template.substitute({
        'imports': import_strings,
        'all': all_strings,
    }))
    text_file.close()


class ModuleInspector:

    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module = import_module(f"arcade.{module_name}")

        self._classes = []
        self._attributes = []
        self._functions = []

        self.inspect()

    @property
    def classes(self):
        return sorted([
            (name, value.__module__[7:])
            for name, value in self._classes
        ])

    @property
    def functions(self):
        return sorted([
            (name, value.__module__[7:])
            for name, value in self._functions
        ])

    @property
    def attributes(self):
        return sorted([
            (name, self._module_name)
            for name, _ in self._attributes
        ])

    def inspect(self):
        self._classes = list(self._get_classes())
        self._functions = list(self._get_functions())
        self._attributes = list(self._get_attributes())

    def _get_classes(self):
        for name, value in self._getmembers_filtered():
            if inspect.isclass(value):
                yield (name, value)

    def _get_functions(self):
        for name, value in self._getmembers_filtered():
            if inspect.isfunction(value):
                yield (name, value)

    def _get_attributes(self):
        for name, value in self._getmembers_filtered():
            # Include typing aliases
            if type(value) == typing._GenericAlias:
                yield (name, value)
                continue
            if not inspect.isfunction(value) and not inspect.isclass(value):
                yield (name, value)

    def _getmembers_filtered(self):
        for name, value in inspect.getmembers(self._module):
            # Exclude on name
            if name.startswith("_"):
                continue
            if name in EXCLUDE:
                continue

            if name == "Color":
                print("moo")

            if inspect.isbuiltin(value) or inspect.ismodule(value):
                continue

            # Accept typing aliases
            if type(value) == typing._GenericAlias:
                yield (name, value)
                continue

            module = inspect.getmodule(value)
            # is the module part of the arcade project?
            if module:
                if module != self._module:
                    continue
                if not module.__name__.startswith("arcade."):
                    continue
            else:
                # Now what?
                print("Not in module:", (name, value))

            yield (name, value)


if __name__ == "__main__":
    main()
