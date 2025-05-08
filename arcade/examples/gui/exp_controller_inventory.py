"""

Example of a full functional inventory system.

This example demonstrates how to create a simple inventory system.

Main features are:
- Inventory slots
- Equipment slots
- Move items between slots
- Controller support

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_controller_inventory
"""

# TODO: Drag and Drop

import pyglet.font
from pyglet.event import EVENT_HANDLED
from pyglet.gl import GL_NEAREST
from pyglet.input import Controller

import arcade
from arcade import Rect
from arcade.examples.gui.exp_controller_support_grid import (
    ControllerIndicator,
    setup_grid_focus_transition,
)
from arcade.experimental.controller_window import ControllerWindow, ControllerView
from arcade.gui import (
    Property,
    Surface,
    UIAnchorLayout,
    UIBoxLayout,
    UIFlatButton,
    UIGridLayout,
    UILabel,
    UIOnClickEvent,
    UIView,
    UIWidget,
    bind,
    UIEvent,
)
from arcade.gui.events import UIControllerButtonPressEvent
from arcade.gui.experimental.focus import UIFocusable, UIFocusGroup
from arcade.resources import load_kenney_fonts


class Item:
    """Base class for all items."""

    def __init__(self, symbol: str):
        self.symbol = symbol


class Inventory:
    """
    Basic inventory class.

    Contains items and manages items.


    inventory = Inventory(10)
    inventory.add(Item("🍎"))
    inventory.add(Item("🍌"))
    inventory.add(Item("🍇"))


    for item in inventory:
        print(item.symbol)

    inventory.remove(inventory[0])
    """

    def __init__(self, capacity: int):
        self._items: list[Item | None] = [None for _ in range(capacity)]
        self.capacity = capacity

    def add(self, item: Item):
        empty_slot = None
        for i, slot in enumerate(self._items):
            if slot is None:
                empty_slot = i
                break

        if empty_slot is not None:
            self._items[empty_slot] = item
        else:
            raise ValueError("Inventory is full.")

    def is_full(self):
        return len(self._items) == self.capacity

    def remove(self, item: Item):
        for i, slot in enumerate(self._items):
            if slot == item:
                self._items[i] = None
                return

    def __getitem__(self, index: int):
        return self._items[index]

    def __setitem__(self, index: int, value: Item):
        self._items[index] = value

    def __iter__(self):
        yield from self._items


class Equipment(Inventory):
    """Equipment inventory.

    Contains three slots for head, chest and legs.
    """

    def __init__(self):
        super().__init__(3)

    @property
    def head(self) -> Item:
        return self[0]

    @head.setter
    def head(self, value):
        self[0] = value

    @property
    def chest(self) -> Item:
        return self[1]

    @chest.setter
    def chest(self, value):
        self[1] = value

    @property
    def legs(self) -> Item:
        return self[2]

    @legs.setter
    def legs(self, value):
        self[2] = value


class InventorySlotUI(UIFocusable, UIFlatButton):
    """Represents a single inventory slot.
    The slot accesses a specific index in the inventory.

    Emits an on_click event.
    """

    def __init__(self, inventory: Inventory, index: int, **kwargs):
        super().__init__(size_hint=(1, 1), **kwargs)
        self.ui_label.update_font(font_size=24)
        self._inventory = inventory
        self._index = index

        item = inventory[index]
        if item:
            self.text = item.symbol

    @property
    def item(self) -> Item | None:
        return self._inventory[self._index]

    @item.setter
    def item(self, value):
        self._inventory[self._index] = value
        self._on_item_change()

    def _on_item_change(self, *args):
        if self.item:
            self.text = self.item.symbol
        else:
            self.text = ""


class EquipmentSlotUI(InventorySlotUI):
    pass


class InventoryUI(UIGridLayout):
    """Manages inventory slots.

    Emits an `on_slot_clicked(slot)` event when a slot is clicked.

    """

    def __init__(self, inventory: Inventory, **kwargs):
        super().__init__(
            size_hint=(0.7, 1),
            column_count=6,
            row_count=5,
            align_vertical="center",
            align_horizontal="center",
            vertical_spacing=10,
            horizontal_spacing=10,
            **kwargs,
        )
        self.with_padding(all=10)
        self.with_border(color=arcade.color.WHITE, width=2)

        self.inventory = inventory
        self.grid = {}

        for i, item in enumerate(inventory):
            slot = InventorySlotUI(inventory, i)
            # fill left to right, bottom to top (6x5 grid)
            self.add(slot, column=i % 6, row=i // 6)
            self.grid[(i % 6, i // 6)] = slot
            slot.on_click = self._on_slot_click  # type: ignore

        InventoryUI.register_event_type("on_slot_clicked")

    def _on_slot_click(self, event: UIOnClickEvent):
        # propagate slot click event to parent
        self.dispatch_event("on_slot_clicked", event.source)

    def on_slot_clicked(self, event: UIOnClickEvent):
        pass


class EquipmentUI(UIBoxLayout):
    """Contains three slots for equipment items.

    - Head
    - Chest
    - Legs

    Emits an `on_slot_clicked(slot)` event when a slot is clicked.

    """

    def __init__(self, **kwargs):
        super().__init__(size_hint=(0.3, 1), space_between=10, **kwargs)
        self.with_padding(all=20)
        self.with_border(color=arcade.color.WHITE, width=2)

        equipment = Equipment()

        self.head_slot = self.add(EquipmentSlotUI(equipment, 0))
        self.head_slot.on_click = lambda _: self.dispatch_event("on_slot_clicked", self.head_slot)

        self.chest_slot = self.add(EquipmentSlotUI(equipment, 1))
        self.chest_slot.on_click = lambda _: self.dispatch_event("on_slot_clicked", self.chest_slot)

        self.legs_slot = self.add(EquipmentSlotUI(equipment, 2))
        self.legs_slot.on_click = lambda _: self.dispatch_event("on_slot_clicked", self.legs_slot)

        EquipmentUI.register_event_type("on_slot_clicked")


class ActiveSlotTrackerMixin(UIWidget):
    """
    Mixin class to track the active slot.
    """

    active_slot = Property[InventorySlotUI | None](None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bind(self, "active_slot", self.trigger_render)

    def do_render(self, surface: Surface):
        surface.limit(None)
        if self.active_slot:
            rect: Rect = self.active_slot.rect

            rect = rect.resize(*(rect.size + (2, 2)))
            arcade.draw_rect_outline(rect, arcade.uicolor.RED_ALIZARIN, 2)

        return super().do_render(surface)

    def on_slot_clicked(self, clicked_slot: InventorySlotUI):
        if self.active_slot:
            # disable active slot
            if clicked_slot == self.active_slot:
                self.active_slot = None
                return

            else:
                # swap items
                src_item = self.active_slot.item
                dst_item = clicked_slot.item

                self.active_slot.item = dst_item
                clicked_slot.item = src_item

                self.active_slot = None
                return

        else:
            # activate slot if contains item
            if clicked_slot.item:
                self.active_slot = clicked_slot


class InventoryModal(ActiveSlotTrackerMixin, UIFocusGroup, UIAnchorLayout):
    def __init__(self, inventory: Inventory, **kwargs):
        super().__init__(size_hint=(0.8, 0.8), **kwargs)
        self.with_padding(all=10)
        self.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)
        self._debug = False

        self.add(
            UILabel(text="Inventory", font_size=20, font_name="Kenney Blocks", bold=True),
            anchor_y="top",
        )

        content = UIBoxLayout(size_hint=(1, 0.9), vertical=False, space_between=10)
        self.add(content, anchor_y="bottom")

        inv_ui = content.add(InventoryUI(inventory))
        inv_ui.on_slot_clicked = self.on_slot_clicked  # type: ignore

        eq_ui = content.add(EquipmentUI())
        eq_ui.on_slot_clicked = self.on_slot_clicked  # type: ignore

        # prepare focusable widgets
        widget_grid = inv_ui.grid
        setup_grid_focus_transition(
            widget_grid  # type: ignore
        )  # setup default transitions in a grid

        # add transitions to equipment slots
        cols = max(x for x, y in widget_grid.keys())
        rows = max(y for x, y in widget_grid.keys())

        equipment_slots = [eq_ui.head_slot, eq_ui.chest_slot, eq_ui.legs_slot]

        # connect inventory slots with equipment slots
        slots_to_eq_ratio = (rows + 1) / len(equipment_slots)
        for i in range(rows + 1):
            eq_index = int(i // slots_to_eq_ratio)
            eq_slot = equipment_slots[eq_index]

            inv_slot = widget_grid[(cols, i)]

            inv_slot.neighbor_right = eq_slot
            eq_slot.neighbor_left = inv_slot

        # close button not part of the normal focus rotation, but can be focused with "b"
        self.close_button = self.add(
            # todo: find out why X is not in center
            UIFlatButton(text="X", width=40, height=40),
            anchor_x="right",
            anchor_y="top",
        )
        self.close_button.on_click = lambda _: self.close()  # type: ignore

        # init controller support
        self.detect_focusable_widgets()

    def on_event(self, event: UIEvent) -> bool | None:
        if isinstance(event, UIControllerButtonPressEvent):
            if event.button == "b":
                self.set_focus(self.close_button)
                return EVENT_HANDLED

        return super().on_event(event)

    def close(self):
        self.visible = False
        self.trigger_full_render()


class MyView(UIView, ControllerView):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK

        self.inventory = Inventory(30)

        self.inventory.add(Item("🍎"))
        self.inventory.add(Item("🍌"))
        self.inventory.add(Item("🍇"))

        self.root = self.add_widget(UIAnchorLayout())
        self.add_widget(ControllerIndicator())

        text = self.root.add(
            UILabel(
                text="Open Inventory with 'Select' button on a controller or 'I' key", font_size=24
            )
        )
        text.fit_content()
        text.center_on_screen()

        self._inventory_modal = self.root.add(InventoryModal(self.inventory))

    def toggle_inventory(self):
        self._inventory_modal.visible = not self._inventory_modal.visible

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.I:
            self.toggle_inventory()
            return True

        return super().on_key_press(symbol, modifiers)

    def on_button_press(self, controller: Controller, button):
        if button == "back":
            self.toggle_inventory()
            return True

        return super().on_button_press(controller, button)

    def on_draw_before_ui(self):
        pass


if __name__ == "__main__":
    # pixelate the font
    pyglet.font.base.Font.texture_min_filter = GL_NEAREST
    pyglet.font.base.Font.texture_mag_filter = GL_NEAREST

    load_kenney_fonts()

    ControllerWindow(title="Minimal example", width=1280, height=720, resizable=True).show_view(
        MyView()
    )
    arcade.run()
