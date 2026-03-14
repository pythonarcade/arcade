"""Side panel UI for the HitBox Editor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import arcade
from arcade.gui.widgets import UIWidget, UISpace
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout
from arcade.gui.widgets.text import UIInputText, UILabel
from arcade.hitbox_editor.canvas import REGION_COLORS

if TYPE_CHECKING:
    from arcade.hitbox_editor.state import EditorState, ToolMode


PANEL_BG_COLOR = (40, 40, 45, 240)
SECTION_LABEL_COLOR = (180, 180, 180, 255)
ACTIVE_BUTTON_BG = (70, 130, 180, 255)
INACTIVE_BUTTON_BG = (50, 50, 55, 255)


class SidePanel(UIBoxLayout):
    """Side panel with controls for the hitbox editor."""

    def __init__(
        self,
        state: EditorState,
        on_load_texture: Callable[[], None],
        on_load_hitbox: Callable[[], None],
        on_save_json: Callable[[], None],
        on_tool_change: Callable[[str], None],
        on_region_select: Callable[[str], None],
        on_region_add: Callable[[str], None],
        on_region_remove: Callable[[], None],
        width: float = 300,
    ) -> None:
        super().__init__(
            vertical=True,
            space_between=4,
            size_hint=(None, 1.0),
        )
        self.rect = self.rect.resize(width=width)
        self.with_background(color=PANEL_BG_COLOR)
        self.with_padding(all=8)

        self._state = state
        self._on_load_texture = on_load_texture
        self._on_load_hitbox = on_load_hitbox
        self._on_save_json = on_save_json
        self._on_tool_change = on_tool_change
        self._on_region_select = on_region_select
        self._on_region_add = on_region_add
        self._on_region_remove = on_region_remove

        # References to dynamic widgets
        self._region_list_container: UIBoxLayout | None = None
        self._tool_buttons: dict[str, UIFlatButton] = {}
        self._region_name_input: UIInputText | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the full panel UI."""
        # --- File section ---
        self.add(UILabel(text="FILE", font_size=10, text_color=SECTION_LABEL_COLOR))

        file_row = UIBoxLayout(vertical=False, space_between=4, size_hint=(1.0, None))
        file_row.rect = file_row.rect.resize(height=32)

        load_tex_btn = UIFlatButton(text="Load Texture", width=136, height=32)
        load_tex_btn.on_click = lambda _: self._on_load_texture()
        file_row.add(load_tex_btn)

        load_hb_btn = UIFlatButton(text="Load HitBox", width=136, height=32)
        load_hb_btn.on_click = lambda _: self._on_load_hitbox()
        file_row.add(load_hb_btn)

        self.add(file_row)
        self.add(UISpace(height=8))

        # --- Tool section ---
        self.add(UILabel(text="TOOL", font_size=10, text_color=SECTION_LABEL_COLOR))

        tool_row = UIBoxLayout(vertical=False, space_between=4, size_hint=(1.0, None))
        tool_row.rect = tool_row.rect.resize(height=32)

        for tool_name in ("add", "select", "delete"):
            btn = UIFlatButton(text=tool_name.capitalize(), width=90, height=32)
            btn.on_click = lambda _, t=tool_name: self._on_tool_change(t)
            self._tool_buttons[tool_name] = btn
            tool_row.add(btn)

        self.add(tool_row)
        self.add(UISpace(height=8))

        # --- Export section ---
        self.add(UILabel(text="EXPORT", font_size=10, text_color=SECTION_LABEL_COLOR))

        save_btn = UIFlatButton(text="Save JSON", width=280, height=32)
        save_btn.on_click = lambda _: self._on_save_json()
        self.add(save_btn)
        self.add(UISpace(height=8))

        # --- Region section ---
        self.add(UILabel(text="REGIONS", font_size=10, text_color=SECTION_LABEL_COLOR))

        # Add region controls (above the list so they stay in a fixed position)
        add_region_row = UIBoxLayout(vertical=False, space_between=4, size_hint=(1.0, None))
        add_region_row.rect = add_region_row.rect.resize(height=32)

        self._region_name_input = UIInputText(width=170, height=32, text="")
        add_region_row.add(self._region_name_input)

        add_btn = UIFlatButton(text="+", width=40, height=32)
        add_btn.on_click = lambda _: self._handle_add_region()
        add_region_row.add(add_btn)

        remove_btn = UIFlatButton(text="-", width=40, height=32)
        remove_btn.on_click = lambda _: self._on_region_remove()
        add_region_row.add(remove_btn)

        self.add(add_region_row)

        # Region list (grows downward as the last section, nothing below to overlap)
        self._region_list_container = UIBoxLayout(
            vertical=True, space_between=2, size_hint=(1.0, None)
        )
        self.add(self._region_list_container)

    def _handle_add_region(self) -> None:
        """Handle adding a new region from the input field."""
        if self._region_name_input is None:
            return
        name = self._region_name_input.text.strip()
        if name:
            self._on_region_add(name)
            self._region_name_input.text = ""

    def refresh_region_list(self) -> None:
        """Rebuild the region list buttons."""
        if self._region_list_container is None:
            return

        self._region_list_container.clear()

        for idx, name in enumerate(self._state.regions):
            is_active = name == self._state.active_region
            point_count = len(self._state.regions[name])
            region_color = REGION_COLORS[idx % len(REGION_COLORS)]

            if is_active:
                label = f"> {name} ({point_count} pts)"
            else:
                label = f"  {name} ({point_count} pts)"

            btn = UIFlatButton(
                text=label,
                width=280,
                height=28,
            )
            if is_active:
                btn.with_background(color=ACTIVE_BUTTON_BG)
                btn.with_border(width=3, color=region_color)
            btn.on_click = lambda _, n=name: self._on_region_select(n)
            self._region_list_container.add(btn)

    def refresh_tool_buttons(self) -> None:
        """Update tool button highlighting based on current tool mode."""
        active_border = (200, 200, 255, 255)
        current = self._state.tool_mode.value
        for tool_name, btn in self._tool_buttons.items():
            if tool_name == current:
                btn.with_background(color=ACTIVE_BUTTON_BG)
                btn.with_border(width=2, color=active_border)
            else:
                btn.with_background(color=INACTIVE_BUTTON_BG)
                btn.with_border(width=0, color=(0, 0, 0, 0))


