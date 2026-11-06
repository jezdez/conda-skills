from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins import hookimpl

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace
    from collections.abc import Iterator

    from conda.plugins.types import CondaSubcommand


def configure_parser(parser: ArgumentParser) -> None:
    """Add skill subcommands and options without loading their implementations."""
    from .cli.parser import (
        configure_init,
        configure_install,
        configure_list,
        configure_quickstart,
        configure_remove,
        configure_status,
    )

    subparsers = parser.add_subparsers(dest="skill_command", required=True)
    configure_list(subparsers)
    configure_status(subparsers)
    configure_install(subparsers)
    configure_remove(subparsers)
    configure_init(subparsers)
    configure_quickstart(subparsers)


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
