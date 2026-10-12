import json
import os
import gc
from .config_element import ConfigElement
from ..logger import Logger
from ..data_container import DataContainer, Favourite, get_nested, set_nested_path
from tools import DC

logger = Logger('ConfigLoader', 'info')


class ConfigLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_dir):
        elements = []
        for file in get_files(config_dir):
            elements += load_file(config_dir, file)
        elements = progress(elements)

        if elements:
            raise Exception(f'Unresolved dependencies: {[e.key for e in elements]}')

        logger.info('ConfigLoader: Done')
        gc.collect()


def get_files(config_dir):
    return [f for f in os.listdir(config_dir) if f.endswith('.json')]


def load_file(config_dir, file):
    with open(f'{config_dir}/{file}') as f:
        data = json.load(f)
    elements = []
    for k, v in data.items():
        if v.get('class') == 'DataContainer':
            init_container(k, v)
        elif v.get('class') == 'Favourite':
            init_favourite(k, v)
        else:
            elements.append(ConfigElement(key=k, **v))
    return progress(elements)


def progress(elements):
    made_progress = True
    while made_progress:
        made_progress = False
        for element in elements:
            if element.progress():
                made_progress = True
        elements = [e for e in elements if not e.done()]
    return elements


def init_container(key, config):
    container = get_nested(key) or set_nested_path(key, DataContainer())
    if config.get('icon'):
        container.icon = config['icon']
    if config.get('name'):
        container.name = config['name']


def init_favourite(key, config):
    values = config.get('values', {})
    fav = Favourite(icon=config.get('icon'), name=config.get('name'), cards=values.get('cards', []))
    name = key.split('.')[-1]
    setattr(DC().favourites, name, fav)
