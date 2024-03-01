import pytest
import arcade


@pytest.fixture
def instance() -> arcade.Text:
    return arcade.Text("Initial text", 0.0, 0.0)


@pytest.mark.parametrize(
    ("prop_name", "prop_new_value"),
    (
        ("value", "New test value"),
        ("x", 12.0),
        ("y", 12.0),
        ("font_name", "Times New Roman"),
        ("font_size", 20.0),
        ("width", 600),
        ("bold", True),
        ("italic", True),
        ("rotation", 45.0)
    )
)
def test_text_instance_simple_property(ctx, instance, prop_name, prop_new_value):

    assert getattr(instance, prop_name) != prop_new_value
    setattr(instance, prop_name, prop_new_value)
    assert getattr(instance, prop_name) == prop_new_value


@pytest.mark.parametrize(
    ("prop_name", "valid_values"),
    (
        ("anchor_x", ("left", "center", "right")),
        ("anchor_y", ("top", "center", "baseline", "bottom")),
        ("bold", (True, False))
    )
)
def test_text_instance_discrete_prop_valid_values(ctx, prop_name, valid_values):

    for value in valid_values:
        i = arcade.Text("Initial text", 0.0, 0.0)

        setattr(i, prop_name, value)
        assert getattr(i, prop_name) == value


def test_text_instance_multiline_setter(ctx):

    # this requires width to be set or pyglet.label will throw errors

    instance = arcade.Text("Initial text", 0.0, 0.0, width=400)
    instance.multiline = True

    assert instance.multiline


@pytest.mark.parametrize("align", ("center", "right"))
def test_text_instance_align_not_left(ctx, align):

    # width must be set
    instance = arcade.Text("Initial text", 0, 0, width=500)

    assert instance.align != align
    instance.align = align

    assert instance.align == align

    # Multiline value should not be influenced by align like in 2.X
    assert instance.multiline is False


def test_text_instance_position_setter(instance):

    instance.position = (20.0, 40.0)
    assert instance.x == 20.0
    assert instance.y == 40.0


def test_text_instance_position_getter():

    instance = arcade.Text("Initial text", 20.0, 40.0)
    assert instance.position == (20.0, 40.0)
