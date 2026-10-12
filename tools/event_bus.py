import asyncio
from tools import Component


def _is_coroutine(obj):
    return hasattr(obj, 'send') and hasattr(obj, 'throw') and hasattr(obj, '__name__')


class EventBus(Component):
    METADATA = {
        'paused': {'type': bool, 'label': 'Global Pause', 'init': True, 'read': True, 'write': True, 'default': False, 'widget': 'toggle'},
    }

    def __init__(self, name='EventBus', loglevel='info', **kwargs):
        Component.__init__(self, name, loglevel, **kwargs)
        self.subscribers = {}
        self.paused_events = set()
        self.info('EventBus: Initialized')

    def subscribe(self, event_name, action, condition=True):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []

        self.subscribers[event_name].append((action, condition))
        self.debug(f'EventBus: Subscribed to \'{event_name}\' (total: {len(self.subscribers[event_name])})')

    def subscribe_once(self, event_name, action, condition=True):
        def wrapper(*args, **kwargs):
            self.unsubscribe(event_name, wrapper)
            result = action(*args, **kwargs)
            if _is_coroutine(result):
                asyncio.create_task(result)

        self.subscribe(event_name, wrapper, condition)
        self.debug(f'EventBus: Subscribed once to \'{event_name}\'')

    def publish(self, event_name, *args, **kwargs):
        if self.paused:
            return
        if event_name in self.paused_events:
            return
        if event_name not in self.subscribers:
            return

        if self.t_on:
            self.trace(f'EventBus: Publishing \'{event_name}\' to {len(self.subscribers[event_name])} handlers')

        for action, condition in self.subscribers[event_name]:
            should_run = condition() if callable(condition) else condition
            if should_run:
                result = action(*args, **kwargs)
                if _is_coroutine(result):
                    asyncio.create_task(result)

    def unsubscribe(self, event_name, action):
        if event_name not in self.subscribers:
            return

        original_count = len(self.subscribers[event_name])
        self.subscribers[event_name] = [
            (act, cond) for act, cond in self.subscribers[event_name]
            if act != action
        ]

        if not self.subscribers[event_name]:
            del self.subscribers[event_name]
            self.debug(f'EventBus: Unsubscribed from \'{event_name}\' (event removed)')
        elif len(self.subscribers[event_name]) < original_count:
            self.debug(f'EventBus: Unsubscribed from \'{event_name}\' (remaining: {len(self.subscribers[event_name])})')

    def unsubscribe_all(self, action):
        for event_name in list(self.subscribers.keys()):
            self.unsubscribe(event_name, action)
        self.debug('EventBus: Unsubscribed action from all events')

    def clear(self, event_name=None):
        if event_name is None:
            count = len(self.subscribers)
            self.subscribers.clear()
            self.debug(f'EventBus: Cleared all events ({count} total)')
        elif event_name in self.subscribers:
            del self.subscribers[event_name]
            self.debug(f'EventBus: Cleared \'{event_name}\'')

    def pause_event(self, event_name):
        self.paused_events.add(event_name)
        self.debug(f'EventBus: Paused event \'{event_name}\'')

    def resume_event(self, event_name):
        self.paused_events.discard(event_name)
        self.debug(f'EventBus: Resumed event \'{event_name}\'')

    def __str__(self):
        event_counts = {name: len(subs) for name, subs in self.subscribers.items()}
        return f'EventBus(events={event_counts})'
