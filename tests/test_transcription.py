from pathlib import Path

from steve_thought_capture.models import PreparedAudio
from steve_thought_capture.transcription import transcribe_audio


class DummyContext(dict):
    pass


def test_transcribe_audio_returns_transcript_result(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.ogg"
    audio_path.write_bytes(b"ogg")
    out_base = tmp_path / "sample"
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("hello world\n")

    prepared = PreparedAudio(
        original_audio_path=str(audio_path),
        prepared_audio_path=str(audio_path),
        original_format="ogg",
        prepared_format="ogg",
        conversion_performed=False,
    )
    context = DummyContext(asr={"backend": "whisper_cpp", "whisper_cpp": {"model_name": "large-v3-turbo", "binary_path": "/bin/echo", "model_path": "/tmp/model.bin", "language_mode": "auto"}})

    monkeypatch.setattr("steve_thought_capture.transcription._output_base_for_audio", lambda path: out_base)

    def fake_run(cmd):
        return None

    monkeypatch.setattr("steve_thought_capture.transcription._run_whisper_cpp", fake_run)
    monkeypatch.setattr("steve_thought_capture.transcription.Path.exists", lambda self: True)
    monkeypatch.setattr("steve_thought_capture.transcription.Path.read_text", lambda self: "hello world\n")

    result = transcribe_audio(prepared, context)

    assert result.success is True
    assert result.raw_text == "hello world"
    assert result.backend == "whisper_cpp"


def test_transcribe_audio_returns_clear_error_for_missing_binary(tmp_path):
    audio_path = tmp_path / "sample.ogg"
    audio_path.write_bytes(b"ogg")
    prepared = PreparedAudio(str(audio_path), str(audio_path), "ogg", "ogg", False)
    context = DummyContext(asr={"backend": "whisper_cpp", "whisper_cpp": {"model_name": "large-v3-turbo", "binary_path": "/missing/whisper-cli", "model_path": "/tmp/model.bin", "language_mode": "auto"}})

    result = transcribe_audio(prepared, context)

    assert result.success is False
    assert "binary" in result.error.lower()


def test_transcribe_audio_surfaces_command_failure(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.ogg"
    audio_path.write_bytes(b"ogg")
    prepared = PreparedAudio(str(audio_path), str(audio_path), "ogg", "ogg", False)
    fake_bin = tmp_path / "whisper-cli"
    fake_model = tmp_path / "model.bin"
    fake_bin.write_text("bin")
    fake_model.write_text("model")
    context = DummyContext(asr={"backend": "whisper_cpp", "whisper_cpp": {"model_name": "large-v3-turbo", "binary_path": str(fake_bin), "model_path": str(fake_model), "language_mode": "auto"}})

    def fail_run(cmd):
        raise RuntimeError("boom")

    monkeypatch.setattr("steve_thought_capture.transcription._run_whisper_cpp", fail_run)

    result = transcribe_audio(prepared, context)

    assert result.success is False
    assert "boom" in result.error
