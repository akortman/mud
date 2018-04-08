'''
A span is a range of musical events, particularly notes and rests.
'''

from event import Event
from notation import Duration, Rest, Note, Pitch, Time

class Span(object):
    def __init__(self, events, offset=None, length=None, sort=True):
        '''
        events must be a list of Events, or a list of (e, t) tuples,
        where e is a the object wrapped by the event (Note, Rest, etc)
        and   t is a duration (the offset from the start of the span)
        '''
        self._events = []
        assert type(offset) is int or type(offset) is float or type(offset) is Time
        self._offset = Time(offset)
        for e in events:
            if type(e) is Event:
                self.append_event(e)
            else:
                assert type(e[1]) is Time
                self.append_event(Event(e[0], e[1]))
        if length is not None:
            actual_length = self.calculate_span_length()
            assert actual_length <= length + 0.0001
            self.pad_to_length(length)
            assert actual_length >= length - 0.0001
        if sort:
            self.sort()

    def append_event(self, event):
        events_requiring_nonzero_duration = { Note, Rest }
        if (type(event) in events_requiring_nonzero_duration
            and event.duration.is_zero()):
            # disallow events with 0 duration from being in the Span
            return
        self._events.append(event)

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

    def num_events(self):
        return len(self._events)

    def length(self):
        return Time(self.calculate_span_length())

    def offset(self):
        return self._offset

    def sort(self):
        self._events.sort(key=lambda e: e.time().in_beats())

    def __getitem__(self, key):
        return self._events[key]

    def __iter__(self):
        return self._events.__iter__()

    def __str__(self):
        return ('Span[length={}, offset={}, ('
                .format(self.calculate_span_length(), self._offset)
                + ', '.join(str(e) for e in self._events)
                + ')]')

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        raise NotImplementedError