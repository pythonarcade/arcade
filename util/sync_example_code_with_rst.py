from pathlib import Path

# .. literalinclude:: ../../arcade/examples/array_backed_grid_buffered.py
# :ref:`platformer_tutorial`
import re
literal_include_pattern = re.compile(r"literalinclude:: .*/(.*\.py)$")
ref_pattern = re.compile(":ref:`(.*)`")


class Processor:
    def __init__(self):
        self.file_list = []
        self.file_reference_list = []
        self.links_to_rst_files = []

    def check_python_file(self, cur_node: Path):
        # print(f"File: {cur_node}")
        if cur_node.name.endswith(".py"):
            if cur_node.name in self.file_list:
                print(f"Duplicate file {cur_node.name}")
            else:
                self.file_list.append(cur_node.name)

    def check_directory_for_python_files(self, my_path: Path):
        for cur_node in my_path.iterdir():
            if cur_node.is_dir():
                self.check_directory_for_python_files(cur_node)
            else:
                self.check_python_file(cur_node)

    def check_rst_file(self, cur_node: Path):
        if cur_node.name.endswith(".rst"):

            i = 0
            try:
                for i, line in enumerate(open(cur_node, encoding="utf-8")):
                    for match in re.finditer(literal_include_pattern, line):
                        self.file_reference_list.append(match.group(1))
                        # print('Found on line %s: %s' % (i + 1, match.group(1)))
            except:
                print(f"Error reading {cur_node} - {i}")

    def check_for_rst_ref(self, cur_node: Path):
        if cur_node.name.endswith(".rst"):

            i = 0
            try:
                for i, line in enumerate(open(cur_node, encoding="utf-8")):
                    for match in re.finditer(ref_pattern, line):
                        self.links_to_rst_files.append(match.group(1))
                        # print('Found on line %s: %s' % (i + 1, match.group(1)))
            except:
                print(f"Error reading {cur_node} - {i}")

    def check_directory_for_rst_files(self, my_path: Path):
        for cur_node in my_path.iterdir():
            if cur_node.is_dir():
                self.check_directory_for_rst_files(cur_node)
            else:
                self.check_rst_file(cur_node)

    def check_directory_for_rst_files2(self, my_path: Path):
        for cur_node in my_path.iterdir():
            if cur_node.is_dir():
                self.check_directory_for_rst_files2(cur_node)
            else:
                self.check_for_rst_ref(cur_node)

    def check_for_unused_python_files(self):
        error = False
        for file in self.file_list:
            if file not in self.file_reference_list:
                print(f"{file}")
                error = True
        if not error:
            print("No issues found.")

    def check_for_no_refs(self):
        error = False
        for file in self.file_list:
            short_file = file[:-3]
            if short_file not in self.links_to_rst_files:
                print(f"{file}")
                error = True
        if not error:
            print("No issues found.")


def main():
    processor = Processor()
    processor.check_directory_for_python_files(Path("../arcade/examples/"))
    processor.check_directory_for_rst_files(Path("../doc/"))
    processor.check_directory_for_rst_files2(Path("../doc/"))
    print()
    print("Files not in any .rst file:")
    print("---------------------------")
    processor.check_for_unused_python_files()

    print()
    print("Files not referenced:")
    print("-----------------------")
    processor.check_for_no_refs()


main()
