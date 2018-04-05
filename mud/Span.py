'''
A span is a range of musical events, particularly notes and rests.
'''

from Event import Event
from Notation import *

class Span(object):
    def __init__(self, events, length=None, pad_to_length=True, sorted=True):
        '''
        events must be a list of Events, or a list of (e, t) tuples,
        where e is a the object wrapped by the event (Note, Rest, etc)
        and   t is a duration (the offset from the start of the span)
        '''
        self._events = []
        for e in events:
            if type(e) is Event:
                self._events.append(e)
            else:
                assert type(e[1]) is Duration
                self._events.append(Event(e[0], e[1]))
        if length is not None:
            actual_length = self.calculate_span_length()
            assert actual_length <= length + 0.0001
            if pad_to_length:
                self.pad_to_length(length)
            assert actual_length >= length - 0.0001
        if sorted:
            self.sort()

    def calculate_span_length(self):
        end_positions = [event.time().in_beats()
                         + event.unwrap().duration().in_beats()
                         for event in self._events]
        return max(end_positions)

    def pad_to_length(self, length):
        actual_length = self.calculate_span_length()
        if length < actual_length:
            return
        to_pad = length - actual_length
        if to_pad <= 0:
            return
        self._events.append(Event(Rest(to_pad), Duration(actual_length)))

    def length(self):
        return self.calculate_span_length()

    def sort(self):
        self._events.sort(key=lambda e: e.time().in_beats())

    def __getitem__(self, key):
        return self._events[key]

    def __iter__(self):
        return self._events.__iter__()

    def __str__(self):
        return 'Span[' + ', '.join(str(e) for e in self._events) + ']'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        raise NotImplementedError