'''
defaults for mud
'''

_defaults_dict = {
    'resolution': 1.0 / 16.0,
}

class _Settings(object):
    def __init__(self, **kwargs):
        for key in kwargs:
            self.__dict__['_{}'.format(key)] = kwargs[key]

    @property
    def resolution(self):
        return self._resolution

settings = _Settings(**_defaults_dict)