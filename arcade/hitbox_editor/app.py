"""Main application view for the HitBox Editor."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from arcade.gui import UIView
from arcade.gui.widgets.layout import UIAnchorLayout

from arcade.hitbox_editor.canvas import CanvasRenderer
from arcade.hitbox_editor.context_menu import ContextMenu
from arcade.hitbox_editor.history import (
    AddRegionCommand,
    Clipboard,
    CommandHistory,
    CompositeCommand,
    RemovePointCommand,
    RemoveRegionCommand,
)
from arcade.hitbox_editor.panel import SidePanel
from arcade.hitbox_editor.state import EditorState, ToolMode
from arcade.hitbox_editor.tools import (
    AddTool,
    BaseTool,
    DeleteTool,
    SelectTool,
    MOUSE_LEFT,
    MOUSE_MIDDLE,
    MOUSE_RIGHT,
)

PANEL_WIDTH = 300


class HitBoxEditorView(UIView):
    """The main view for the HitBox Editor application."""

    def __init__(
        self,
        texture_path: str | Path | None = None,
        hitbox_path: str | Path | None = None,
    ) -> None:
        super().__init__()
        self.background_color = (30, 30, 35, 255)

        # State
        self.state = EditorState()
        self.state.history = CommandHistory()
        self.state.clipboard = Clipboard()

        # Tools
        self._tools: dict[ToolMode, BaseTool] = {
            ToolMode.ADD: AddTool(),
            ToolMode.SELECT: SelectTool(),
            ToolMode.DELETE: DeleteTool(),
        }

        # Canvas
        self.canvas = CanvasRenderer(self.state, self.window)

        # Context menu state
        self._context_menu: ContextMenu | None = None

        # Track space key for pan-drag
        self._space_held = False

        # Build side panel
        self._panel = SidePanel(
            state=self.state,
            on_load_texture=self._on_load_texture,
            on_load_hitbox=self._on_load_hitbox,
            on_save_json=self._on_save_json,
            on_tool_change=self._on_tool_change,
            on_region_select=self._on_region_select,
            on_region_add=self._on_region_add,
            on_region_remove=self._on_region_remove,
        )

        # Layout: anchor panel to right
        anchor = self.add_widget(UIAnchorLayout())
        anchor.add(self._panel, anchor_x="right", anchor_y="top")

        # Load initial files if provided
        if texture_path is not None:
            self.state.load_texture(texture_path)
            self.canvas.fit_texture(PANEL_WIDTH)
        if hitbox_path is not None:
            self.state.load_hitbox(hitbox_path)

        self._refresh_panel()

    def on_show_view(self) -> None:
        super().on_show_view()
        # Re-attach canvas to current window
        self.canvas.window = self.window

    def on_draw_before_ui(self) -> None:
        """Draw the canvas (texture + polygons) before GUI elements."""
        self.canvas.draw(PANEL_WIDTH)

    def on_draw_after_ui(self) -> None:
        """Draw status text overlaid on the top-right of the canvas area."""
        self.window.default_camera.use()
        text = self._build_status_text()
        canvas_right = self.window.width - PANEL_WIDTH - 8
        top = self.window.height - 8
        arcade.draw_text(
            text,
            canvas_right, top,
            color=(200, 200, 200, 200),
            font_size=10,
            anchor_x="right",
            anchor_y="top",
        )

    def _in_canvas(self, x: float) -> bool:
        """Check if x coordinate is in the canvas area (not the panel)."""
        return x < self.window.width - PANEL_WIDTH

    @property
    def _active_tool(self) -> BaseTool:
        return self._tools[self.state.tool_mode]

    # --- Mouse events ---

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        # Dismiss context menu on any click
        if self._context_menu is not None:
            self._dismiss_context_menu()
            return

        if not self._in_canvas(x):
            return  # Let UIManager handle panel clicks

        if button == MOUSE_RIGHT:
            wx, wy = self.canvas.screen_to_world(x, y)
            self._show_context_menu(x, y, wx, wy)
            return

        if button == MOUSE_LEFT and not self._space_held:
            wx, wy = self.canvas.screen_to_world(x, y)
            self._update_pick_threshold()
            self._active_tool.on_press(self.state, wx, wy, button, modifiers)
            self._refresh_panel()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == MOUSE_LEFT and self._in_canvas(x):
            wx, wy = self.canvas.screen_to_world(x, y)
            self._active_tool.on_release(self.state, wx, wy, button, modifiers)
            self._refresh_panel()

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> None:
        # Pan with middle mouse button or left+space
        if (buttons & MOUSE_MIDDLE) or (buttons & MOUSE_LEFT and self._space_held):
            self.canvas.pan(dx, dy)
            return

        if (buttons & MOUSE_LEFT) and self._in_canvas(x):
            # Convert screen delta to world delta for the tool
            # We need world-space delta, not screen-space delta
            wx1, wy1 = self.canvas.screen_to_world(x - dx, y - dy)
            wx2, wy2 = self.canvas.screen_to_world(x, y)
            world_dx = wx2 - wx1
            world_dy = wy2 - wy1
            self._active_tool.on_drag(self.state, wx2, wy2, world_dx, world_dy)

    def on_mouse_scroll(
        self, x: int, y: int, scroll_x: int, scroll_y: int
    ) -> None:
        if self._in_canvas(x):
            factor = 1.1 if scroll_y > 0 else 1 / 1.1
            self.canvas.zoom_at(factor, x, y)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        if self._in_canvas(x):
            wx, wy = self.canvas.screen_to_world(x, y)
            self.state.cursor_world = (wx, wy)

    # --- Keyboard events ---

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        ctrl = modifiers & arcade.key.MOD_CTRL
        shift = modifiers & arcade.key.MOD_SHIFT

        if symbol == arcade.key.SPACE:
            self._space_held = True
            return

        # Tool switching: 1/2/3
        if symbol == arcade.key.KEY_1:
            self._on_tool_change("add")
        elif symbol == arcade.key.KEY_2:
            self._on_tool_change("select")
        elif symbol == arcade.key.KEY_3:
            self._on_tool_change("delete")

        # Fit view
        elif symbol == arcade.key.F:
            self.canvas.fit_texture(PANEL_WIDTH)

        # Undo/Redo
        elif symbol == arcade.key.Z and ctrl and shift:
            self._do_redo()
        elif symbol == arcade.key.Z and ctrl:
            self._do_undo()
        elif symbol == arcade.key.Y and ctrl:
            self._do_redo()

        # Copy/Cut/Paste
        elif symbol == arcade.key.C and ctrl:
            self._do_copy()
        elif symbol == arcade.key.X and ctrl:
            self._do_cut()
        elif symbol == arcade.key.V and ctrl:
            self._do_paste()

        # Select all
        elif symbol == arcade.key.A and ctrl:
            self._do_select_all()

        # Delete selected
        elif symbol in (arcade.key.DELETE, arcade.key.BACKSPACE):
            self._do_delete_selected()

        # Save
        elif symbol == arcade.key.S and ctrl:
            self._on_save_json()

        self._refresh_panel()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.SPACE:
            self._space_held = False

    def _update_pick_threshold(self) -> None:
        """Update point pick threshold based on current zoom level."""
        # 10 pixels in screen space, converted to world units
        self.state.pick_threshold = 10.0 / max(self.canvas.zoom, 0.01)

    # --- Actions ---

    def _do_undo(self) -> None:
        if self.state.history:
            self.state.history.undo(self.state)

    def _do_redo(self) -> None:
        if self.state.history:
            self.state.history.redo(self.state)

    def _do_copy(self) -> None:
        if self.state.clipboard:
            self.state.clipboard.copy(self.state)

    def _do_cut(self) -> None:
        if self.state.clipboard:
            self.state.clipboard.cut(self.state)

    def _do_paste(self) -> None:
        if self.state.clipboard:
            self.state.clipboard.paste(self.state)

    def _do_select_all(self) -> None:
        if self.state.active_region and self.state.active_region in self.state.regions:
            self.state.selected_points.clear()
            for i in range(len(self.state.regions[self.state.active_region])):
                self.state.selected_points.add((self.state.active_region, i))

    def _do_delete_selected(self) -> None:
        if not self.state.selected_points or self.state.history is None:
            return
        removals = []
        for region_name, index in sorted(self.state.selected_points, reverse=True):
            if region_name in self.state.regions and index < len(
                self.state.regions[region_name]
            ):
                point = self.state.regions[region_name][index]
                removals.append(RemovePointCommand(region_name, index, point))

        if removals:
            cmd = CompositeCommand(removals, "Delete selected")
            self.state.history.execute(cmd, self.state)
            self.state.selected_points.clear()

    # --- Context menu ---

    def _show_context_menu(
        self, screen_x: float, screen_y: float, world_x: float, world_y: float
    ) -> None:
        """Show a context menu at the given screen position."""
        self._dismiss_context_menu()

        # If right-clicking near a point, select it first
        self._update_pick_threshold()
        nearest = self.state.find_nearest_point(
            world_x, world_y, self.state.pick_threshold
        )
        if nearest is not None:
            key = (nearest[0], nearest[1])
            if key not in self.state.selected_points:
                self.state.selected_points.clear()
                self.state.selected_points.add(key)
                self.state.active_region = nearest[0]

        self._context_menu = ContextMenu(
            state=self.state,
            ui_manager=self.ui,
            x=screen_x,
            y=screen_y,
            on_dismiss=self._dismiss_context_menu,
            world_x=world_x,
            world_y=world_y,
        )
        self.ui.add(self._context_menu, layer=10)

    def _dismiss_context_menu(self) -> None:
        """Remove the context menu."""
        if self._context_menu is not None:
            self.ui.remove(self._context_menu)
            self._context_menu = None
        self._refresh_panel()

    # --- Panel callbacks ---

    def _on_load_texture(self) -> None:
        path = _open_file_dialog(
            "Open Texture",
            [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")],
        )
        if path:
            self.state.load_texture(path)
            self.canvas.fit_texture(PANEL_WIDTH)
            self._refresh_panel()

    def _on_load_hitbox(self) -> None:
        path = _open_file_dialog(
            "Open HitBox",
            [("JSON files", "*.json *.json.gz"), ("All files", "*.*")],
        )
        if path:
            self.state.load_hitbox(path)
            self._refresh_panel()

    def _on_save_json(self) -> None:
        if not self.state.regions:
            return
        path = _save_file_dialog(
            "Save HitBox",
            [("JSON files", "*.json"), ("Compressed JSON", "*.json.gz"), ("All files", "*.*")],
            default_extension=".json",
        )
        if path:
            self.state.to_hitbox().save(path)

    def _on_tool_change(self, tool_name: str) -> None:
        mode = ToolMode(tool_name)
        self.state.tool_mode = mode
        self._refresh_panel()

    def _on_region_select(self, name: str) -> None:
        self.state.active_region = name
        self.state.selected_points.clear()
        self._refresh_panel()

    def _on_region_add(self, name: str) -> None:
        if name in self.state.regions or self.state.history is None:
            return
        cmd = AddRegionCommand(name)
        self.state.history.execute(cmd, self.state)
        self._refresh_panel()

    def _on_region_remove(self) -> None:
        if self.state.active_region is None or self.state.history is None:
            return
        name = self.state.active_region
        points = list(self.state.regions.get(name, []))
        cmd = RemoveRegionCommand(name, points)
        self.state.history.execute(cmd, self.state)
        self._refresh_panel()

    def _refresh_panel(self) -> None:
        """Refresh all dynamic panel elements."""
        self._panel.refresh_region_list()
        self._panel.refresh_tool_buttons()

    def _build_status_text(self) -> str:
        """Build the status text string."""
        parts = []
        cx, cy = self.state.cursor_world
        parts.append(f"({cx:.1f}, {cy:.1f})")

        if self.state.active_region:
            pts = len(self.state.regions.get(self.state.active_region, []))
            parts.append(f"Region: {self.state.active_region} ({pts} pts)")

        sel = len(self.state.selected_points)
        if sel:
            parts.append(f"Selected: {sel}")

        parts.append(f"Tool: {self.state.tool_mode.value}")
        parts.append(f"Zoom: {self.canvas.zoom:.1f}x")

        return " | ".join(parts)


def _open_file_dialog(
    title: str, filetypes: list[tuple[str, str]]
) -> str | None:
    """Open a file dialog using tkinter (stdlib)."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        return path if path else None
    except Exception:
        return None


def _save_file_dialog(
    title: str,
    filetypes: list[tuple[str, str]],
    default_extension: str = ".json",
) -> str | None:
    """Open a save file dialog using tkinter (stdlib)."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=default_extension,
        )
        root.destroy()
        return path if path else None
    except Exception:
        return None
