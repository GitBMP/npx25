"""
Microdot-based webserver for MicroPython IoT.

Usage:
    server = WebServer(port=80, logger=Logger('WebServer'))
"""

import asyncio, gc

from tools import Component, DC, DataContainer, Logger
from tools.data_container import get_nested, Favourite
#from .meta import get_cards, get_values, set_values
from microdot.microdot import Microdot, send_file


dc = DC()

class WebServer(Logger):
    def __init__(self, port=80, name='WebServer', loglevel='info'):
        Logger.__init__(self, name, loglevel)
        self.port = port
        self.app = Microdot()
        self._create_routes()
        self._start_webserver()
        self.info(f'WebServer: Initialized on port {port}')

    def _start_webserver(self):
        """Starts the webserver as an async task"""
        server = asyncio.create_task(self.app.start_server(port=self.port, debug=False))
        self.info(f'WebServer: Async server task created on port {self.port}')

    def _create_routes(self):
        """Creates all route handlers"""

        # HTML route
        @self.app.route('/')
        async def index(request):
            self.info('WebServer: Route hit: /')
            return send_file('app/index.html')

        # API routes
        @self.app.route('/api/sidebar', methods=['GET'])
        async def api_sidebar(request):
            self.info('WebServer: API hit: /api/sidebar')
            result = [
                
            ]
            return dc.get_containers()

        @self.app.route('/api/cards', methods=['POST'])
        async def api_cards(request):
            self.info('WebServer: API hit: /api/cards')
            path = request.json.get('path')
            if path is None:
                return {'error': 'Missing path'}, 400

            container = get_nested(path)
            if not isinstance(container, DataContainer):
                self.warning(f'api_cards: Invalid path "{path}"')
                return {'error': 'Invalid path'}, 400

            return container.get_cards()


        @self.app.route('/api/get', methods=['POST'])
        async def api_get(request):
            self.info('WebServer: API hit: /api/get')
            paths = request.json
            result = {}

            for path in paths:
                parts = path.split('.')
                attr_name = parts.pop()
                nav_path = 'dc.' + '.'.join(parts)
                value = component = None

                try:
                    component = eval(nav_path, {'dc': dc})
                except Exception as e:
                    self.warning(f'api_get: Failed to get "{path}": {e}')
                
                if isinstance(component, Component):
                    value = component.get_value(attr_name)
                
                result[path] = value

            return result

        @self.app.route('/api/set', methods=['POST'])
        async def api_set(request):
            self.info('WebServer: API hit: /api/set')
            data = request.json

            for path, value in data.items():
                parts = path.split('.')
                attr_name = parts.pop()
                nav_path = 'dc.' + '.'.join(parts)

                try:
                    component = eval(nav_path, {'dc': dc})
                except Exception as e:
                    self.warning(f'api_set: Failed to set "{path}": {e}')
                    continue

                if isinstance(component, (Component, Favourite)):
                    component.set_value(value, attr_name)

            return None

        # Static file catch-all (lowest priority)
        @self.app.route('/<path:path>')
        async def static_files(request, path):
            gc.collect()
            self.info(f'WebServer: Static file request ({gc.mem_free()}): /{path}')
            try:
                return send_file(f'app/{path}')
            except Exception as e:
                self.warning(f'WebServer: Failed to serve app/{path}: {e}')
                return {'error': 'Not found'}, 404