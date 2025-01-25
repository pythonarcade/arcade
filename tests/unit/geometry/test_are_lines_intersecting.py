from arcade.geometry import are_lines_intersecting


def test_are_lines_intersecting():
    line_a = [(0, 0), (50, 50)]
    line_b = [(0, 0), (50, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    # Two lines clearly intersecting
    line_a = [(0, 0), (50, 50)]
    line_b = [(0, 50), (50, 0)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    # Two parallel lines clearly not intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(0, 50), (0, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False

    # Two lines intersecting at the edge points
    line_a = [(0, 0), (50, 0)]
    line_b = [(0, -50), (0, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is True

    # Two perpendicular lines almost intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(-1, -50), (-1, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False

    # Twp perpendicular lines almost intersecting
    line_a = [(0, 0), (50, 0)]
    line_b = [(51, -50), (51, 50)]
    assert are_lines_intersecting(*line_a, *line_b) is False
