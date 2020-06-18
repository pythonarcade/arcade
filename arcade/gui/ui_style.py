from pathlib import Path
from typing import Dict, Any, Sequence

import yaml

from arcade.gui.utils import parse_value
from arcade.resources import resolve_resource_path


class UIStyle:
    """
    Used as singleton in the UIView, style changes are applied by changing the values of the singleton.

    Use `.load()` to update UIStyle instance from YAML-file


    """
    __default_style = None

    def __init__(self, data: Dict, **kwargs):
        self.data = data

    @staticmethod
    def from_file(path: Path):
        """
        Load style from a file, overwriting existing data

        :param path: Path to a valid style YAML file
        """
        ui_style = UIStyle({})
        ui_style.load(path)
        return ui_style

    def load(self, path: Path):
        with path.open() as file:
            data: Dict[str, Dict[str, Any]] = yaml.safe_load(file)
            assert isinstance(data, dict)

        # parse values, expected structure Dict[class, Dict[key, value]]
        for style_class, style_data in data.items():
            for key, value in style_data.items():
                style_data[key] = parse_value(value)

        self.data = data

    @classmethod
    def default_style(cls):
        """
        :return: empty style # TODO maybe load the real default style once
        """
        if cls.__default_style is None:
            cls.__default_style = UIStyle.from_file(resolve_resource_path(
                ':resources:style/default.yml'
            ))
        return cls.__default_style

    def get_class(self, style_classes: str):
        return self.data.setdefault(style_classes, {})

    def set_class_attrs(self, style_classes: str, **kwargs):
        style_data = self.get_class(style_classes)
        for key, value in kwargs.items():
            if value is None:
                if key in style_data:
                    del style_data[key]
            else:
                style_data[key] = value

    def get_attr(self, style_classes: Sequence[str], attr: str):
        """
        Retrieves an attribute, resolved from style by style_classes

        :param style_classes: List of style classes, resolving from right to left
        :param attr: attribute name to get value for
        :return: value of the attribute, first found
        """
        for style_class in reversed(style_classes):
            style_data = self.data.get(style_class, {})
            attr_value = style_data.get(attr)
            if attr_value:
                return attr_value
        else:
            return None
