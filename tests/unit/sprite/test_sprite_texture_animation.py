import math
import pytest
import arcade


@pytest.fixture(scope="module")
def keyframes():
    """Create a list of keyframes."""
    return [
        arcade.TextureKeyframe(
            texture=arcade.load_texture(
                f":assets:/images/animated_characters/female_adventurer/femaleAdventurer_walk{i}.png"
            ),
            duration=1000,
        )
        for i in range(8)
    ]


def test_create(keyframes):
    """Test creation and initial state"""
    sprite = arcade.TextureAnimationSprite()
    anim = arcade.TextureAnimation(keyframes=keyframes)
    sprite.animation = anim

    assert sprite.animation == anim
    assert sprite.time == 0.0

    assert anim.num_frames == 8
    assert anim.duration_ms == 8000
    assert anim.duration_seconds == 8.0

    # Was the initial texture set?
    assert sprite.texture == keyframes[0].texture


def test_animation(keyframes):
    """Test animation class"""
    anim = arcade.TextureAnimation(keyframes=keyframes)

    # Get keyframes at specific times (0.5s increments)
    for i in range(16):
        time = i / 2
        index = i // 2
        assert anim.get_keyframe(time) == (index, keyframes[index])

    # Looping
    assert anim.get_keyframe(8.0) == (0, keyframes[0])
    # Not looping (should clamp to last frame)
    assert anim.get_keyframe(10.0, loop=False) == (7, keyframes[7])


def test_animating_sprite(keyframes):
    """Test animating sprite using time"""
    sprite = arcade.TextureAnimationSprite()
    anim = arcade.TextureAnimation(keyframes=keyframes)
    sprite.animation = anim
    assert sprite.time == 0.0

    steps = 16
    delta_time = 0
    for i in range(steps):
        index = i // 2
        if i > 0:
            delta_time = 0.5
        sprite.update_animation(delta_time)
        assert sprite.texture == keyframes[index].texture

    # Looping
    sprite.time = 8.0
    sprite.update_animation(0.0)
    assert sprite.texture == keyframes[0].texture

    # Not looping
    sprite.time = 8.0
    sprite.update_animation(0.0, loop=False)
