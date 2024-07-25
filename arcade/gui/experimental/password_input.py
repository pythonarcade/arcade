from __future__ import annotations

from typing import Optional

from arcade.gui import Surface, UIEvent, UIInputText, UITextEvent


class UIPasswordInput(UIInputText):
    """A password input field. The text is hidden with asterisks."""

    def on_event(self, event: UIEvent) -> Optional[bool]:
        """Override to remove new lines from the input, which are not allowed in passwords."""
        if isinstance(event, UITextEvent):
            event.text = event.text.replace("\n", "").replace("\r", "")  # remove new lines!
        return super().on_event(event)

    def do_render(self, surface: Surface):
        """Override to render the text as asterisks."""
        self.layout.begin_update()
        position = self.caret.position
        text = self.text
        self.text = "*" * len(self.text)
        super().do_render(surface)
        self.text = text
        self.caret.position = position
        self.layout.end_update()
