"""
A player standing on moving platforms in PhysicsEnginePlatformer moves with
them. Standing across two platforms used to move it by both their speeds
added together, so it slid along until it stood on only one (#2782).
"""

import pytest

import arcade

PLATFORM_WIDTH = 64
SIZE = 32


def _platforms(*speeds):
    """A row of touching platforms with their tops at y = 32."""
    platforms = arcade.SpriteList()
    for i, speed in enumerate(speeds):
        platform = arcade.SpriteSolidColor(
            PLATFORM_WIDTH, 32, center_x=100 + i * PLATFORM_WIDTH, center_y=16
        )
        platform.change_x = speed
        platforms.append(platform)
    return platforms


def _run(player_x, *speeds, frames=30):
    platforms = _platforms(*speeds)
    player = arcade.SpriteSolidColor(SIZE, SIZE, center_x=player_x, center_y=48)
    engine = arcade.PhysicsEnginePlatformer(player, platforms=platforms, gravity_constant=1)
    for _ in range(frames):
        engine.update()
    return player, platforms


@pytest.mark.parametrize("speed", [2, -3])
def test_one_platform(speed):
    player, platforms = _run(100, speed)
    assert player.center_x == pytest.approx(100 + 30 * speed)
    assert player.bottom == pytest.approx(platforms[0].top)


@pytest.mark.parametrize("speed", [2, -3])
@pytest.mark.parametrize("count", [2, 4])
def test_across_platforms_moving_together(speed, count):
    # Centered on the seam between the first two platforms
    player, platforms = _run(132, *[speed] * count)
    assert player.center_x == pytest.approx(132 + 30 * speed)
    assert player.bottom == pytest.approx(platforms[0].top)


@pytest.mark.parametrize(
    ("player_x", "expected_change"),
    [
        # Mostly on the left platform, which moves right
        (120, 2),
        # Mostly on the right platform, which moves left
        (144, -2),
    ],
)
def test_across_platforms_moving_apart(player_x, expected_change):
    player, _ = _run(player_x, 2, -2, frames=1)
    assert player.center_x == pytest.approx(player_x + expected_change)


def test_moving_platform_next_to_still_one():
    # Mostly on a still platform, a little on a moving one
    player, _ = _run(120, 0, 2, frames=1)
    assert player.center_x == pytest.approx(120)
    # Mostly on the moving one
    player, _ = _run(144, 0, 2, frames=1)
    assert player.center_x == pytest.approx(146)
