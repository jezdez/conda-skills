from __future__ import annotations

from pathlib import Path


def test_skill_forge_recording_uses_an_explicit_temporary_prefix() -> None:
    """Avoid conda name lookup finding and replacing an unrelated environment."""
    tape = (Path(__file__).parents[1] / "demos/skill-forge.tape").read_text(
        encoding="utf-8"
    )
    assert "conda create -y -p ../skills " in tape
    assert 'Type "conda activate ../skills"' in tape
    assert "conda create -y -n " not in tape
