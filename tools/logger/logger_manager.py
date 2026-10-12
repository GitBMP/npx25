"""
Global logger manager - singleton for handler management and message routing.

Usage:
    lm = LoggerManager()
    lm.add_handler(print_handler)
    lm.log('System started', 'Main', 3)
"""

import time

# Log level constants
LEVEL_MAP = {
    'critical': 0,
    'error': 1,
    'warning': 2,
    'info': 3,
    'debug': 4,
    'trace': 5
}

LEVEL_NAMES = {
    0: 'Critical',
    1: 'Error',
    2: 'Warning',
    3: 'Info',
    4: 'Debug',
    5: 'Trace'
}


class LoggerManager:
    """Singleton manager for log handlers and message routing"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._handlers = []

    def add_handler(self, handler):
        """Add a log handler function"""
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler):
        """Remove a log handler function"""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def get_timestamp(self):
        """Generate timestamp string in HH:MM:SS.mmm format"""
        ms = time.ticks_ms()
        total_seconds = ms // 1000
        ms_remainder = ms % 1000

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{ms_remainder:03d}'

    def log(self, message, name, loglevel, logger_level=None, path=''):
        """Route log message to all handlers"""
        loglevel = LEVEL_MAP.get(loglevel.lower(), 3) if isinstance(loglevel, str) else loglevel
        logger_level = LEVEL_MAP.get(logger_level.lower(), 3) if isinstance(logger_level, str) else logger_level

        if logger_level is not None and loglevel > logger_level:
            return

        timestamp = self.get_timestamp()

        for handler in self._handlers:
            handler(message, name, loglevel, timestamp, path)
