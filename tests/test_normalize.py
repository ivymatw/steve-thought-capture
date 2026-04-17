from steve_thought_capture.normalize import normalize_transcript


class DummyContext(dict):
    pass


def test_normalize_collapses_whitespace():
    context = DummyContext(lexicon={"proper_nouns": []}, correction_map={"substitutions": {}})
    result = normalize_transcript("  hello   world  ", context)
    assert result.normalized_text == "hello world"


def test_normalize_converts_simplified_to_traditional():
    context = DummyContext(lexicon={"proper_nouns": []}, correction_map={"substitutions": {}})
    result = normalize_transcript("麦克风测试", context)
    assert result.normalized_text == "麥克風測試"


def test_normalize_applies_correction_map():
    context = DummyContext(
        lexicon={"proper_nouns": ["Anthropic", "Opus"]},
        correction_map={"substitutions": {"and topic opus": "Anthropic Opus"}},
    )
    result = normalize_transcript("and topic opus", context)
    assert result.normalized_text == "Anthropic Opus"


def test_normalize_preserves_mixed_language_text():
    context = DummyContext(lexicon={"proper_nouns": []}, correction_map={"substitutions": {}})
    result = normalize_transcript("幫我看一下 OpenAI Realtime API", context)
    assert result.normalized_text == "幫我看一下 OpenAI Realtime API"
