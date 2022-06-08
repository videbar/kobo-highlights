"""This module contains the definitions of the rich console objects used in the entire
program.
"""
from rich.console import Console

console = Console(color_system="auto")
error_console = Console(stderr=True, style="bold red")
