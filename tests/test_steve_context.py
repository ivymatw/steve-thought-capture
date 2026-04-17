from pathlib import Path

import pytest
import yaml


REQUIRED_CONFIGS = [
    "asr.yaml",
    "lexicon.yaml",
    "correction_map.yaml",
    "routing_preferences.yaml",
    "project_aliases.yaml",
]


def test_all_required_config_files_exist(project_root):
    config_dir = project_root / "configs"
    for name in REQUIRED_CONFIGS:
        assert (config_dir / name).exists(), name


def test_config_files_have_expected_top_level_keys(project_root):
    config_dir = project_root / "configs"
    expected = {
        "asr.yaml": {"backend", "whisper_cpp"},
        "lexicon.yaml": {"proper_nouns"},
        "correction_map.yaml": {"substitutions"},
        "routing_preferences.yaml": {"keywords"},
        "project_aliases.yaml": {"aliases"},
    }
    for name, keys in expected.items():
        data = yaml.safe_load((config_dir / name).read_text())
        assert keys.issubset(set(data.keys())), name


def test_load_steve_context_reads_all_configs(project_root):
    from steve_thought_capture.steve_context import load_steve_context

    context = load_steve_context(project_root)

    assert context["asr"]["backend"] == "whisper_cpp"
    assert "Anthropic" in context["lexicon"]["proper_nouns"]
    assert context["correction_map"]["substitutions"] == {}
    assert context["routing_preferences"]["keywords"] == {
        "note_capture": [],
        "task_capture": [],
        "knowledge_capture": [],
        "project_artifact_input": [],
    }
    assert context["project_aliases"]["aliases"] == {}


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]
