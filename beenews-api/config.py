import yaml
import os

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class BeeNewsConfiguration(dict):
    def __init__(self, *args, **kwargs):
        super(BeeNewsConfiguration, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def from_file(cls):
        config_file = os.getenv('BEENEWS_CONFIG', 'settings.yml')
        if not config_file.startswith('/'):
            path = os.path.dirname(os.path.abspath(__file__))
            config_file = '/'.join((path, config_file))
        with open(config_file, 'r') as conf:
            config = yaml.load(conf, Loader=Loader)
            return cls(config)

    def __getitem__(self, key):
        return super(BeeNewsConfiguration, self).__getitem__(key)

    def __setitem__(self, key, value):
        return super(BeeNewsConfiguration, self).__setitem__(key, value)

config = BeeNewsConfiguration.from_file()


def get_app_conf():
    return BeeNewsConfiguration.from_file()
