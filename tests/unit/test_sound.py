import wave
from pathlib import Path

import pytest
from pyglet.media.codecs.base import StaticSource, StreamingSource
from pyglet.media.codecs.wave import WAVEDecodeException, WaveDecoder

import arcade

frame_count = 0
player = None


@pytest.mark.parametrize("load", [arcade.Sound, arcade.load_sound])
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("path_kind", ["path", "resource"])
def test_sound_explicit_decoder(load, streaming, path_kind, tmp_path, mocker):
    if path_kind == "path":
        # An explicit decoder must work without a registered file extension.
        path = tmp_path / "sound.custom"
        with wave.open(str(path), "wb") as audio:
            audio.setparams((1, 1, 8000, 80, "NONE", "not compressed"))
            audio.writeframes(b"\x80" * 80)
    else:
        path = ":resources:sounds/laser1.wav"

    decoder = WaveDecoder()
    decode = mocker.spy(decoder, "decode")
    sound = load(path, streaming, decoder=decoder)

    decode.assert_called_once()
    assert decode.call_args.args == (sound.file_name, None)
    assert decode.call_args.kwargs["streaming"] is streaming
    assert Path(sound.file_name).is_file()
    assert sound.source.duration > 0
    assert sound.source.audio_format.channels > 0
    assert isinstance(sound.source, StreamingSource if streaming else StaticSource)

    source = sound.source.get_queue_source()
    audio_data = source.get_audio_data(1024)
    assert audio_data is not None
    assert audio_data.length > 0
    if path_kind == "path":
        assert sound.source.duration == pytest.approx(0.01)
        assert sound.source.audio_format.sample_rate == 8000
        assert audio_data.data == b"\x80" * 80


@pytest.mark.parametrize("load", [arcade.Sound, arcade.load_sound])
@pytest.mark.parametrize("streaming", [False, True])
def test_sound_explicit_decoder_failure(load, streaming, mocker):
    decoder = WaveDecoder()
    error = WAVEDecodeException("Explicit decoder failed")
    decode = mocker.patch.object(decoder, "decode", side_effect=error)

    # This valid WAV would load successfully if automatic decoders were tried.
    expected_error = WAVEDecodeException if load is arcade.Sound else FileNotFoundError
    with pytest.raises(expected_error, match="Explicit decoder failed") as exc:
        load(":resources:sounds/laser1.wav", streaming, decoder=decoder)

    decode.assert_called_once()
    if load is arcade.Sound:
        assert exc.value is error
    else:
        assert exc.value.__cause__ is error


def test_sound_normal_load_and_playback(window):
    global frame_count, player

    laser_wav = arcade.load_sound(":resources:sounds/laser1.wav")
    laser_mp3 = arcade.load_sound(":resources:sounds/laser1.mp3")

    laser_wav_stream = arcade.load_sound(":resources:sounds/laser1.wav", streaming=True)
    laser_mp3_stream = arcade.load_sound(":resources:sounds/laser1.mp3", streaming=True)

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

        if frame_count == 60:
            player = laser_mp3.play(volume=0.5)
            assert laser_mp3.get_volume(player) == 0.5
            laser_mp3.set_volume(1.0, player)
            assert laser_mp3.get_volume(player) == 1.0

        if frame_count == 80:
            assert laser_mp3.is_playing(player) is True
            laser_mp3.stop(player)
            assert laser_mp3.is_playing(player) is False

            player = laser_mp3_stream.play(volume=0.5)
            assert laser_mp3_stream.get_volume(player) == 0.5
            laser_mp3_stream.set_volume(1.0, player)
            assert laser_mp3_stream.get_volume(player) == 1.0

        if frame_count == 100:
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
