from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins import hookimpl

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace
    from collections.abc import Iterator

    from conda.plugins.types import CondaSubcommand


def configure_parser(parser: ArgumentParser) -> None:
    """Add skill subcommands and options without loading their implementations."""
    from conda.cli.helpers import add_parser_json, add_parser_prefix

    subparsers = parser.add_subparsers(dest="skill_command", required=True)
    for command in ("list", "status", "install", "remove"):
        child = subparsers.add_parser(
            command, help=f"{command.capitalize()} skill links."
        )
        add_parser_json(child)
        if command != "status":
            add_parser_prefix(child)
        if command != "list":
            child.add_argument(
                "--backend", choices=("agents", "claude"), default="agents"
            )
            child.add_argument(
                "--global",
                dest="global_scope",
                action="store_true",
                help="Use your home directory instead of the current project.",
            )
        if command in ("install", "remove"):
            child.add_argument("skill_name", help="Packaged skill directory name.")


def run(args: Namespace) -> int:
    """Load the CLI on invocation and return its exit status for parsed args."""
    from .cli.main import execute

    return execute(args)


@hookimpl
def conda_subcommands() -> Iterator[CondaSubcommand]:
    """Register conda skill with lazy command execution."""
    from conda.plugins.types import CondaSubcommand

    yield CondaSubcommand(
        name="skill",
        summary="Link conda-packaged agent skills into client directories.",
        configure_parser=configure_parser,
        action=run,
    )
