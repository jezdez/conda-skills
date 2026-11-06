from __future__ import annotations

from typing import TYPE_CHECKING

from conda.cli.helpers import add_parser_json, add_parser_prefix

if TYPE_CHECKING:
    from argparse import ArgumentParser, _SubParsersAction


def configure_list(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure package-owned source skill listing."""
    summary = "List package-owned skills in the source environment."
    parser = subparsers.add_parser("list", help=summary, description=summary)
    add_parser_json(parser)
    add_parser_prefix(parser)


def configure_status(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure destination status without a source environment selector."""
    summary = "Show destination entries."
    parser = subparsers.add_parser("status", help=summary, description=summary)
    add_parser_json(parser)
    backends = parser.add_mutually_exclusive_group()
    backends.add_argument("--backend", choices=("agents", "claude"), default="agents")
    backends.add_argument(
        "--all",
        action="store_true",
        dest="all_backends",
        help="Show both agents and claude destinations in the selected scope.",
    )
    _add_global_option(parser)


def configure_install(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure linking a packaged skill into a client directory."""
    summary = "Link a packaged skill into a client directory."
    parser = subparsers.add_parser("install", help=summary, description=summary)
    add_parser_json(parser)
    add_parser_prefix(parser)
    _add_destination_options(parser)
    parser.add_argument("skill_name", help="Packaged skill directory name.")


def configure_remove(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure removal of a matching packaged skill link."""
    summary = "Remove a matching skill link."
    parser = subparsers.add_parser("remove", help=summary, description=summary)
    add_parser_json(parser)
    add_parser_prefix(parser)
    _add_destination_options(parser)
    parser.add_argument("skill_name", help="Packaged skill directory name.")


def _add_destination_options(parser: ArgumentParser) -> None:
    """Add the shared client backend and explicit home-directory scope."""
    parser.add_argument("--backend", choices=("agents", "claude"), default="agents")
    _add_global_option(parser)


def _add_global_option(parser: ArgumentParser) -> None:
    """Require an explicit flag to authorize home-directory writes."""
    parser.add_argument(
        "--global",
        dest="global_scope",
        action="store_true",
        help="Use your home directory instead of the current project.",
    )


def configure_init(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure scriptable skill skeleton creation without environment lookup."""
    summary = "Create a skill authoring skeleton and conda recipe."
    parser = subparsers.add_parser("init", help=summary, description=summary)
    add_parser_json(parser)
    _add_global_option(parser)
    parser.add_argument("skill_name", metavar="NAME", help="New skill directory name.")
    parser.add_argument(
        "--description", help="When to use the skill; defaults to a placeholder."
    )


def configure_quickstart(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """Configure the interactive guide, preserving conda source selection."""
    summary = "Run an interactive guide to create or link a skill."
    parser = subparsers.add_parser("quickstart", help=summary, description=summary)
    add_parser_json(parser)
    add_parser_prefix(parser)
    _add_global_option(parser)
