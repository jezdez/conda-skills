"""Sphinx configuration for conda-skills documentation."""

from __future__ import annotations

project = html_title = "conda-skills"
extensions = ["myst_parser", "sphinx_design"]
myst_enable_extensions = ["colon_fence"]
html_theme = "conda_sphinx_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/jezdez/conda-skills",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        }
    ],
    "use_edit_page_button": True,
}
html_context = {
    "github_user": "jezdez",
    "github_repo": "conda-skills",
    "github_version": "main",
    "doc_path": "docs",
}
html_baseurl = "https://jezdez.github.io/conda-skills/"
exclude_patterns = ["_build", "superpowers", "**/superpowers", "examples"]
