from tools import Component, Logger

state_logger = Logger('State', loglevel='warning')


class State:
    def __init__(self, name, on_enter=None, on_exit=None):
        self.name = name
        self.on_enter = on_enter
        self.on_exit = on_exit
        state_logger.info(f'State: Created state \'{name}\'')

    def enter(self):
        state_logger.debug(f'State: Entering \'{self.name}\'')
        self.execute_func(self.on_enter)

    def exit(self):
        state_logger.debug(f'State: Exiting \'{self.name}\'')
        self.execute_func(self.on_exit)

    def __str__(self):
        return f'State({self.name})'

    @staticmethod
    def execute_func(func):
        if callable(func):
            func()
        elif isinstance(func, list):
            for f in func:
                State.execute_func(f)


class StateMachine(Component):
    METADATA = {
        'state': {'type': str, 'label': 'Current State', 'read': True, 'write': True, 'widget': 'select', 'set': 'transition', 'get': 'state', 'update': True},
        'prev': {'widget': 'button_row', 'icon': 'icon-skip-previous', 'label': 'Navigation', 'write': True, 'read': False, 'group': 'state_nav'},
        'next': {'widget': 'button_row', 'icon': 'icon-skip-next', 'label': 'Navigation', 'write': True, 'read': False, 'group': 'state_nav'},
    }

    def __init__(self, name='StateMachine', loglevel='info', **kwargs):
        Component.__init__(self, name, loglevel, **kwargs)
        self.states = {}
        self.state_order = []
        self.current_state = None
        self.current_index = 0
        self.info('StateMachine: Initialized')

    def add_state(self, name, on_enter=None, on_exit=None):
        state = State(name, on_enter, on_exit)
        self.states[name] = state
        self.state_order.append(name)

        if self.current_state is None:
            self.current_state = state
            self.info(f'StateMachine: Initial state set to \'{name}\'')
            state.enter()
        else:
            self.debug(f'StateMachine: Added state \'{name}\'')

        self.meta['state']['choices'] = self.state_order

    def transition(self, state_name):
        if state_name not in self.states:
            self.warning(f'StateMachine: Transition to unknown state \'{state_name}\' failed')
            return False

        old_state = self.current_state.name if self.current_state else None

        if self.current_state:
            self.current_state.exit()

        self.current_state = self.states[state_name]
        self.current_index = self.state_order.index(state_name)
        self.current_state.enter()

        self.info(f'StateMachine: Transitioned from \'{old_state}\' to \'{state_name}\'')
        return True

    def state(self):
        return self.current_state.name if self.current_state else None

    def next(self):
        if not self.state_order:
            return
        self.current_index = (self.current_index + 1) % len(self.state_order)
        self.transition(self.state_order[self.current_index])

    def prev(self):
        if not self.state_order:
            return
        self.current_index = (self.current_index - 1) % len(self.state_order)
        self.transition(self.state_order[self.current_index])

    def __str__(self):
        return f'StateMachine(current={self.state()}, states={self.state_order})'
