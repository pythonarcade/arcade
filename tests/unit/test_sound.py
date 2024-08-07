from pathlib import Path

import pytest

import arcade

frame_count = 0
player = None


def test_sound_normal_load_and_playback(window):
    global frame_count, player

    laser_wav = arcade.load_sound(":resources:sounds/laser1.wav")
    laser_mp3 = arcade.load_sound(":resources:sounds/laser1.mp3")
    laser_ogg = arcade.load_sound(":resources:sounds/laser1.ogg")

    laser_wav_stream = arcade.load_sound(":resources:sounds/laser1.wav", streaming=True)
    laser_mp3_stream = arcade.load_sound(":resources:sounds/laser1.mp3", streaming=True)
    laser_ogg_stream = arcade.load_sound(":resources:sounds/laser1.ogg", streaming=True)

    frame_count = 0

    def update(dt):
        global frame_count, player
        frame_count += 1

        if frame_count == 1:
            player = laser_wav.play(volume=0.5)
            assert laser_wav.get_volume(player) == 0.5
            laser_wav.set_volume(1.0, player)
            assert laser_wav.get_volume(player) == 1.0

        if frame_count == 20:
            assert laser_wav.is_playing(player) is True
            laser_wav.stop(player)
            assert laser_wav.is_playing(player) is False

            player = laser_wav_stream.play(volume=0.5)
            assert laser_wav_stream.get_volume(player) == 0.5
            laser_wav_stream.set_volume(1.0, player)
            assert laser_wav_stream.get_volume(player) == 1.0

        if frame_count == 40:
            assert laser_wav_stream.is_playing(player) is True
            laser_wav_stream.stop(player)
            assert laser_wav_stream.is_playing(player) is False

            player = laser_ogg.play(volume=0.5)
            assert laser_ogg.get_volume(player) == 0.5
            laser_ogg.set_volume(1.0, player)
            assert laser_ogg.get_volume(player) == 1.0

        if frame_count == 60:
            assert laser_ogg.is_playing(player) is True
            laser_ogg.stop(player)
            assert laser_ogg.is_playing(player) is False

            player = laser_ogg_stream.play(volume=0.5)
            assert laser_ogg_stream.get_volume(player) == 0.5
            laser_ogg_stream.set_volume(1.0, player)
            assert laser_ogg_stream.get_volume(player) == 1.0

        if frame_count == 80:
            assert laser_ogg_stream.is_playing(player) is True
            laser_ogg_stream.stop(player)
            assert laser_ogg_stream.is_playing(player) is False

            player = laser_mp3.play(volume=0.5)
            assert laser_mp3.get_volume(player) == 0.5
            laser_mp3.set_volume(1.0, player)
            assert laser_mp3.get_volume(player) == 1.0

        if frame_count == 100:
            assert laser_mp3.is_playing(player) is True
            laser_mp3.stop(player)
            assert laser_mp3.is_playing(player) is False

            player = laser_mp3_stream.play(volume=0.5)
            assert laser_mp3_stream.get_volume(player) == 0.5
            laser_mp3_stream.set_volume(1.0, player)
            assert laser_mp3_stream.get_volume(player) == 1.0

        if frame_count == 120:
            assert laser_mp3_stream.is_playing(player) is True
            laser_mp3_stream.stop(player)
            assert laser_mp3_stream.is_playing(player) is False

    def on_draw():
        window.clear()

    window.on_update = update
    window.on_draw = on_draw
    window.test(140)
    player = None


def test_sound_play_sound_type_errors(window):
    # Non-pathlike raises and provides full loading guidance.
    with pytest.raises(TypeError) as ctx:
        arcade.play_sound(object())
        assert ctx.value.args[0].endswith("arcade.Sound.")

    # Pathlike raises and provides full loading guidance.
    with pytest.raises(TypeError) as ctx:
        arcade.play_sound("file.wav")
        assert ctx.value.args[0].endswidth("play_sound.")

    with pytest.raises(TypeError) as ctx:
        arcade.play_sound(b"file.wav")
        assert ctx.value.args[0].endswidth("play_sound.")

    with pytest.raises(TypeError) as ctx:
        arcade.play_sound(Path("file.wav"))
        assert ctx.value.args[0].endswidth("play_sound.")


def test_sound_stop_sound_type_errors(window):
    sound = arcade.load_sound(":resources:sounds/laser1.wav")

    # Sound raises specific type error
    with pytest.raises(TypeError) as ctx:
        arcade.stop_sound(sound)
        assert ctx.value.args[0].endswith("not the loaded Sound object.")

    with pytest.raises(TypeError) as ctx:
        arcade.play_sound("file.wav")
