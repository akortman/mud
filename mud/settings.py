'''
defaults for mud
'''

from typing import Any

_defaults_dict = {
    'resolution': 1.0 / 8.0, # in quarter notes: these are 32nd notes
}

class _Settings(object):
    def __init__(self, **kwargs):
        self._settings = {
            key: kwargs[key] if key in kwargs else _defaults_dict[key]
            for key in _defaults_dict.keys()
        }

    @property
    def resolution(self):
        return self._settings['resolution']

    def set(self, setting: str, value: Any):
        if setting in _defaults_dict:
            self._settings[setting] = value
        else:
            raise ValueError(f'Unknown setting string `{setting}`')

settings = _Settings(**_defaults_dict)