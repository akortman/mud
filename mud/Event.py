'''
An Event is a musical event:
    - a note or rest
    - a start time relative to the containing span
'''

from Notation import Duration

class Event(object):
    def __init__(self, event, time=None):
        if type(event) is self.__class__:
            self._event = event._event
            self._time = event._time
            if time is not None:
                self._time = time
        else:
            assert time is not None
            self._event = event
            self._time = Duration(time)

    def unwrap(self):
        return self._event

    def time(self):
        return self._time

    def __str__(self):
        return 'Event[{}, time={}]'.format(self._event, self._time)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if type(other) is not Event:
            return False
        return (self._event == other._event
                and self._time == other._time)