"""
Mixin class for callback management.

Usage:
    class Button(AsyncLoop, Callbacks):
        def __init__(self, pin):
            AsyncLoop.__init__(self, time=0.1)
            Callbacks.__init__(self)
            self.pin = pin

        def loop(self):
            if self.duration > 0:
                self.trigger_callbacks()
                self.duration = 0

    button = Button(1)
    button.set_callback(lambda: print('Pressed!'))
"""

from tools import Logger

logger = Logger('Callbacks', loglevel='warning')


class Callbacks:
    METADATA = {
        'trigger_callbacks': {'widget': 'button', 'label': 'Trigger', 'value': 'Trigger', 'write': True, 'read': False},
    }

    def __init__(self):
        self.callbacks = []
        logger.debug('Callbacks: Initialized')

    def set_callback(self, fn_callback):
        """Adds a callback function to the callback list"""
        self.callbacks.append(fn_callback)
        logger.debug(f'Callbacks: Added callback (total: {len(self.callbacks)})')

    def trigger_callbacks(self, *args, **kwargs):
        """Executes all registered callbacks with optional arguments"""
        if logger.t_on:
            logger.trace(f'Callbacks: Triggering {len(self.callbacks)} callbacks')
        for callback in self.callbacks:
            if callback is not None and callable(callback):
                callback(*args, **kwargs)

    def clear_callbacks(self):
        """Removes all callbacks from the list"""
        count = len(self.callbacks)
        self.callbacks.clear()
        logger.debug(f'Callbacks: Cleared {count} callbacks')

    def remove_callback(self, fn_callback):
        """Removes a specific callback function from the list"""
        if fn_callback in self.callbacks:
            self.callbacks.remove(fn_callback)
            logger.debug(f'Callbacks: Removed callback (remaining: {len(self.callbacks)})')
