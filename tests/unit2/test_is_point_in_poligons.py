import arcade


def test_point_in_rectangle():
    poligon = [
        (0, 0),
        (0, 50),
        (50, 50),
        (50, 0),
    ]
    result = arcade.is_point_in_polygon(25, 25, poligon)
    assert result is True


def test_point_not_in_empty_poligon():
    poligon = []
    result = arcade.is_point_in_polygon(25, 25, poligon)
    assert result is False
