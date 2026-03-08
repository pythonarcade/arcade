import argparse
import sys
from typing import Type

from .commands import BaseCommand, InfoCommand


class CLI:
    def __init__(self):
        self.commands: dict[str, BaseCommand] = {}
        self.prog: str = "arcade"
        self.description: str = "Arcade Game Library CLI"

    def register_command(self, command_class: Type[BaseCommand]) -> None:
        command = command_class()  # type: ignore BaseCommand has different constructor than it's implementations
        self.commands[command.name] = command

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        for command_name, command in self.commands.items():
            command_parser = subparsers.add_parser(
                command_name,
                help=command.help,
                description=command.description,
                formatter_class=argparse.RawDescriptionHelpFormatter,
            )
            command.add_arguments(command_parser)

        return parser

    def run(self) -> int:
        parser = self.create_parser()
        args = parser.parse_args()

        if args.command is None:
            parser.print_help()
            return 0

        try:
            command = self.commands[args.command]
            return command.handle(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


def run_arcade_cli():
    cli = CLI()
    cli.register_command(InfoCommand)
    return cli.run()
