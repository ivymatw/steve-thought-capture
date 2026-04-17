from steve_thought_capture.telegram_adapter import run_local_voice_event


def test_run_local_voice_event_passes_audio_through_pipeline(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"wav")
    seen = {}

    def fake_process_voice_event(event, context):
        seen["event"] = event
        seen["context"] = context
        return {"status": "ok", "audio_path": event.audio_path}

    monkeypatch.setattr("steve_thought_capture.telegram_adapter.process_voice_event", fake_process_voice_event)

    result = run_local_voice_event(audio_path, {"mode": "test"})

    assert result == {"status": "ok", "audio_path": str(audio_path.resolve())}
    assert seen["event"].audio_path == str(audio_path.resolve())
    assert seen["event"].mime_type == "audio/wav"
    assert seen["context"] == {"mode": "test"}
