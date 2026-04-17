from pathlib import Path

from steve_thought_capture.audio_prepare import prepare_audio


def test_prepare_audio_converts_telegram_ogg_for_asr(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.ogg"
    audio_path.write_bytes(b"ogg")
    converted = tmp_path / "sample.wav"

    monkeypatch.setattr("steve_thought_capture.audio_prepare._find_ffmpeg", lambda: "/opt/homebrew/bin/ffmpeg")

    def fake_convert(src, dst, ffmpeg_bin):
        converted.write_bytes(b"wav")
        return str(converted)

    monkeypatch.setattr("steve_thought_capture.audio_prepare._convert_with_ffmpeg", fake_convert)

    result = prepare_audio(audio_path)

    assert result.original_audio_path == str(audio_path)
    assert result.prepared_audio_path == str(converted)
    assert result.conversion_performed is True
    assert result.prepared_format == "wav"


def test_prepare_audio_converts_when_format_not_supported(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.m4a"
    audio_path.write_bytes(b"m4a")
    converted = tmp_path / "sample.wav"

    monkeypatch.setattr("steve_thought_capture.audio_prepare._find_ffmpeg", lambda: "/opt/homebrew/bin/ffmpeg")

    def fake_convert(src, dst, ffmpeg_bin):
        converted.write_bytes(b"wav")
        return str(converted)

    monkeypatch.setattr("steve_thought_capture.audio_prepare._convert_with_ffmpeg", fake_convert)

    result = prepare_audio(audio_path)

    assert result.prepared_audio_path == str(converted)
    assert result.conversion_performed is True
    assert result.prepared_format == "wav"


def test_prepare_audio_keeps_wav_input_native(tmp_path):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"wav")

    result = prepare_audio(audio_path)

    assert result.original_audio_path == str(audio_path)
    assert result.prepared_audio_path == str(audio_path)
    assert result.conversion_performed is False
    assert result.prepared_format == "wav"


def test_prepare_audio_raises_clear_error_when_ffmpeg_missing(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.m4a"
    audio_path.write_bytes(b"m4a")

    monkeypatch.setattr("steve_thought_capture.audio_prepare._find_ffmpeg", lambda: None)

    try:
        prepare_audio(audio_path)
    except RuntimeError as exc:
        assert "ffmpeg" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
