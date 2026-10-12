"""
Handler functions for print output.

Usage: LoggerManager().add_handler(print_handler)
"""

from .logger_manager import LEVEL_NAMES


def print_handler(message, name, loglevel, timestamp, path):
    level_str = LEVEL_NAMES.get(loglevel, 'Unknown')
    print(f'{timestamp} {level_str} [{name}]: {message}')
