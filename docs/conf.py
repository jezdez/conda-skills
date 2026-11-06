"""Sphinx configuration for conda-skills documentation."""

from __future__ import annotations

project = html_title = "conda-skills"
extensions = ["myst_parser", "sphinx_design"]
myst_enable_extensions = ["colon_fence"]
html_theme = "conda_sphinx_theme"
exclude_patterns = ["_build", "superpowers", "**/superpowers", "examples"]
