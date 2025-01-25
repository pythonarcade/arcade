from arcade.gui import UIManager, UILayout, Surface


class MockLayout(UILayout):
    call_order = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prepare_render_call = None
        self.prepare_render_count = 0
        self.do_layout_call = None
        self.do_layout_count = 0
        self.render_call = None
        self.render_count = 0

    def prepare_layout(self):
        self.prepare_render_count += 1
        self.prepare_render_call = MockLayout.call_order
        MockLayout.call_order += 1

    def do_layout(self):
        self.do_layout_count += 1
        self.do_layout_call = MockLayout.call_order
        MockLayout.call_order += 1

    def do_render(self, surface: Surface):
        self.render_count += 1
        self.render_call = MockLayout.call_order
        MockLayout.call_order += 1


def test_executes_do_layout_before_draw(window):
    ui = UIManager()
    mock_layout = MockLayout()
    ui.add(mock_layout)

    ui.draw()

    assert mock_layout.prepare_render_call == 0
    assert mock_layout.do_layout_call == 1
    assert mock_layout.render_call == 2
