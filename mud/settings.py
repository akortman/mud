'''
defaults for mud
'''

_defaults_dict = {
    'resolution': 1.0 / 8.0, # in quarter notes: these are 32nd notes
}

class _Settings(object):
    def __init__(self, **kwargs):
        self._resolution = kwargs['resolution']

    @property
    def resolution(self):
        return self._resolution

settings = _Settings(**_defaults_dict)