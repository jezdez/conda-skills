from __future__ import annotations

from pathlib import Path


def test_human_remove_output(prefix: Path, render_cli) -> None:
    render_cli("install", "example", "-p", str(prefix))
    removed = render_cli("remove", "example", "-p", str(prefix))
    assert "Removed link for example." in removed
    absent = render_cli("remove", "example", "-p", str(prefix))
    assert "No link to remove for example." in absent
