import pytest
import arcade


class TestView(arcade.View):
    def __init__(self):
        super().__init__()
        self.on_show_called = False

    def on_show_view(self):
        self.on_show_called = True


def test_window_with_view():
    # Cria uma janela e uma view para o teste
    window = arcade.Window(width=800, height=600, title="Window Test with View")
    view = TestView()

    # Executa o método run com a view
    window.run(view=view)

    # Verifica se a view foi mostrada automaticamente
    assert window.current_view == view
    assert view.on_show_called is True

    # Fecha a janela ao finalizar o teste
    window.close()


def test_run_without_view():
    # Cria uma janela e chama run sem uma view
    window = arcade.Window(width=800, height=600, title="Window Test without View")
    
    # Executa o método run sem uma view
    window.run()

    # Verifica que não há uma view ativa
    assert window.current_view is None

    # Fecha a janela ao finalizar o teste
    window.close()