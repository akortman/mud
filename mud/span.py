'''
A span is a range of musical events, particularly notes and rests.
'''

from event import Event
from notation import Rest, Note, Pitch, Time

class Span(object):
    def __init__(self, events, offset=0, length=None, sort=True):
        '''
        events must be a list of Events, or a list of (e, t) tuples,
        where e is a the object wrapped by the event (Note, Rest, etc)
        and   t is a mud.Time (the offset from the start of the span)
        '''
        self._events = []
        if type(offset) is not int and type(offset) is not float and type(offset) is not Time:
            raise ValueError('Cannot construct offset from value of type {}'.format(type(offset)))
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
        self._events.append(Event(Rest(to_pad), Time(actual_length)))

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

    @classmethod
    def _concat_impl(cls, add_offset, *args):
        def concat_two(span_a, span_b, add_offset):
            if not isinstance(span_a, cls) or not isinstance(span_b, cls):
                raise ValueError('can only concatenate Spans, saw {}, {}'
                                 .format(type(span_a), type(span_b)))
            offset = span_a.length()
            for event in span_b:
                t = event.time()
                if add_offset:
                    t += offset
                e = Event(event.unwrap(), time=t)
                span_a._events.append(e)

            return span_a

        from copy import deepcopy
        result = deepcopy(args[0])
        for span in args[1:]:
            result = concat_two(result, span,add_offset)
        return result
    
    @classmethod
    def concat(cls, *args):
        return cls._concat_impl(True, *args)

    @classmethod
    def overlay(cls, *args):
        raise NotImplementedError
        return cls._concat_impl(False, *args)