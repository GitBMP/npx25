"""
Base class for async looping functionality.

Usage:
    class Button(AsyncLoop):
        def __init__(self, pin):
            AsyncLoop.__init__(self, time=0.1)
            self.pin = pin

        def loop(self):
            # Your loop logic here
            pass

        def _async_on_resume(self):
            # Override to reinitialize state when resumed
            self.duration = 0

    button = Button(pin=1)
    button.async_start()  # Not async - just creates task
"""

import asyncio
from ..logger import Logger

logger = Logger('AsyncLoop', loglevel='warning')


class AsyncLoop:
    METADATA = {
        'async_toggle': {'widget': 'button_row', 'icon': 'icon-play-pause', 'label': 'Async Control', 'write': True, 'read': False, 'group': 'async_control'},
        'async_stop':   {'widget': 'button_row', 'icon': 'icon-stop',       'label': 'Async Control', 'write': True, 'read': False, 'group': 'async_control'},
    }

    def __init__(self, time=0):
        self.time = time
        self._running = False
        self._paused = False
        self._task = None
        logger.debug(f'AsyncLoop: Initialized with time={time}')

    def loop(self):
        """Override this method to implement loop logic"""
        raise NotImplementedError('Subclass must implement loop() method')

    async def _async_loop(self):
        """Internal async loop that continuously calls the loop() method"""
        self._running = True
        while self._running:
            if not self._paused:
                if logger.t_on:
                    logger.trace('AsyncLoop: Executing loop iteration')
                self.loop()
            await asyncio.sleep(self.time)

    def async_start(self):
        """Starts the async loop as a task"""
        if not self._running:
            logger.debug('AsyncLoop: Starting async loop')
            self._task = asyncio.create_task(self._async_loop())

    def async_pause(self):
        """Pauses the async loop (stops calling loop() but keeps task running)"""
        logger.debug('AsyncLoop: Pausing')
        self._async_on_pause()
        self._paused = True

    def async_resume(self):
        """Resumes the async loop after pause"""
        logger.debug('AsyncLoop: Resuming')
        self._paused = False
        self._async_on_resume()

    def _async_on_pause(self):
        """Override to clear state when pausing (e.g., clear pending events)"""
        pass

    def _async_on_resume(self):
        """Override to reinitialize state when resuming (e.g., reset counters)"""
        pass

    def async_toggle(self):
        """Toggles between start/resume and pause."""
        if not self._running:
            self.async_start()
        elif self._paused:
            self.async_resume()
        else:
            self.async_pause()

    def async_stop(self):
        """Stops the async loop completely"""
        logger.debug('AsyncLoop: Stopping')
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
