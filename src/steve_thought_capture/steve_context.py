from __future__ import annotations

from pathlib import Path

import yaml


def load_steve_context(project_root: str | Path) -> dict:
    root = Path(project_root).expanduser().resolve()
    config_dir = root / "configs"
    return {
        "asr": yaml.safe_load((config_dir / "asr.yaml").read_text()),
        "lexicon": yaml.safe_load((config_dir / "lexicon.yaml").read_text()),
        "correction_map": yaml.safe_load((config_dir / "correction_map.yaml").read_text()),
        "routing_preferences": yaml.safe_load((config_dir / "routing_preferences.yaml").read_text()),
        "project_aliases": yaml.safe_load((config_dir / "project_aliases.yaml").read_text()),
    }
