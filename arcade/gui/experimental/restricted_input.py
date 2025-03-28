"""
This is an experimental implementation of a restricted input field.
If the implementation is successful, the feature will be merged into the existing UIInputText class.
"""

from arcade.gui import UIEvent, UIInputText


class UIRestrictedInput(UIInputText):
    """
    A text input field that restricts the input to a certain type.

    This class is meant to be subclassed to create custom input fields
     that restrict the input by providing a custom validation method.

     Invalid inputs are dropped.
    """

    @property
    def text(self):
        """Text of the input field."""
        return self.doc.text

    @text.setter
    def text(self, text: str):
        if not self.validate(text):
            # if the text is invalid, do not update the text
            return

        # we can not call super().text = text here: https://bugs.python.org/issue14965
        UIInputText.text.__set__(self, text)  # type: ignore

    def on_event(self, event: UIEvent) -> bool | None:
        # check if text changed during event handling,
        # if so we need to validate the new text
        old_text = self.text
        pos = self.caret.position

        result = super().on_event(event)
        if not self.validate(self.text):
            self.text = old_text
            self.caret.position = pos

        return result

    def validate(self, text) -> bool:
        """Override this method to add custom validation logic.

        Be aware that an empty string should always be valid.
        """
        return True


class UIIntInput(UIRestrictedInput):
    def validate(self, text) -> bool:
        if text == "":
            return True

        try:
            int(text)
            return True
        except ValueError:
            return False


class UIFloatInput(UIRestrictedInput):
    def validate(self, text) -> bool:
        if text == "":
            return True

        try:
            float(text)
            return True
        except ValueError:
            return False


class UIRegexInput(UIRestrictedInput):
    def __init__(self, *args, pattern: str = r".*", **kwargs):
        super().__init__()
        self.pattern = pattern

    def validate(self, text: str) -> bool:
        if text == "":
            return True

        import re

        return re.match(self.pattern, text) is not None
