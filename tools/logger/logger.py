"""
Logger mixin class for component logging.

Usage as mixin:
    class AnalogSensor(Logger):
        def __init__(self, pin, name='sensor'):
            Logger.__init__(self, name)
            self.info(f'{name} Initialized')
            self.pin = pin

Usage for static files:
    logger = Logger('ConfigLoader')
    def load_config():
        try:pass
        except: logger.critical(f'Failed to load config: {e}')
"""

from .logger_manager import LoggerManager, LEVEL_MAP


class Logger:
    def __init__(self, name, loglevel='info'):
        self.name = name
        self.loglevel = loglevel
        self.logger_manager = LoggerManager()
        self.path = None
        self.t_on = LEVEL_MAP.get(loglevel.lower(), 3) >= 5

    def set_loglevel(self, loglevel):
        self.loglevel = loglevel
        self.t_on = LEVEL_MAP.get(loglevel.lower(), 3) >= 5

    def critical(self, message):
        self.logger_manager.log(message, self.name, 0, self.loglevel, self.path)

    def error(self, message):
        self.logger_manager.log(message, self.name, 1, self.loglevel, self.path)

    def warning(self, message):
        self.logger_manager.log(message, self.name, 2, self.loglevel, self.path)

    def info(self, message):
        self.logger_manager.log(message, self.name, 3, self.loglevel, self.path)

    def debug(self, message):
        self.logger_manager.log(message, self.name, 4, self.loglevel, self.path)

    def trace(self, message):
        self.logger_manager.log(message, self.name, 5, self.loglevel, self.path)
