import argparse
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    name: str
    description: str
    help: str

    def __init__(self, name: str, description: str, help: str) -> None:
        self.name = name
        self.description = description
        self.help = help

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    @abstractmethod
    def handle(self, args: argparse.Namespace) -> int:
        pass
