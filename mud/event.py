'''
An Event is a musical event:
    - a note or rest
    - a start time relative to the containing span
'''

from notation import Time

class Event(object):
    def __init__(self, event, time=None):
        if isinstance(event, Event):
            self._event = event._event
            self._time = event._time
            if time is not None:
                self._time = time
        else:
            if time is None:
                raise ValueError('Can\'t create Event with time as None unless creating from another Event')
            self._event = event
            self._time = Time(time)
        assert type(self._time) is Time

    def duration(self):
        return self._event.duration()

    def pitch(self):
        return self._event.pitch()

    def is_note(self):
        return self._event.is_note()

    def is_rest(self):
        return self._event.is_rest()

    def unwrap(self):
        return self._event

    def time(self):
        return self._time

    def in_span_range(self, range_):
        range_start, range_end = range_
        if range_start >= range_end:
            raise ValueError('invalid range {} to {}'.format(range_start, range_end))
        event_start = self._time.in_beats()
        event_end = self._time.in_beats() + self._event.duration().in_beats()
        if event_start <= range_start and event_end <= range_start:
            return False
        if event_start >= range_end and event_end >= range_end:
            return False
        return True

    # iter for (event, time) unpacking
    def __iter__(self):
        return (self._event, self._time).__iter__()

    def __str__(self):
        return 'Event[{}, time={}]'.format(self._event, self._time)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if type(other) is not Event:
            return False
        return (self._event == other._event
                and self._time == other._time)