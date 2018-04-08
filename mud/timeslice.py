'''
TimeSlice API provides a utility to get the information about all playing notes within a small slice of time.classmethod
'''

from notation import Duration, Time
from event import Event
from span import Span

class SlicedEvent(Event):
    '''
    A sliced event is equivalent to an Event, but may have pre- or
    post-continuations, indicating that the event may start before or after
    the slice.
    '''
    def __init__(self, slice_range, *args):
        super(SlicedEvent, self).__init__(*args)
        self._slice(slice_range)

    def _slice(self, slice_range):
        slice_start, slice_end = slice_range
        event_length = self.unwrap().duration().in_beats()

        self._pre_continue = (self.time().in_beats() < slice_start)
        self._post_continue = (self.time().in_beats() + event_length > slice_end)
        
        if self._post_continue:
            self.unwrap().set_duration(Duration(slice_end - slice_start))
        if self._pre_continue:
            self._time = Time(slice_start)
        assert abs(self.unwrap().duration().in_beats() - (slice_end - slice_start)) < 0.00001

    def is_note_start(self):
        return not self._pre_continue

    def is_note_end(self):
        return not self._post_continue

    def __str__(self):
        return 'SlicedEvent[{}, time={}, start={}, end={}]'.format(
            self._event, self._time, self.is_note_start(), self.is_note_end())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if type(other) is Event:
            if self._pre_continue or self._post_continue:
                return False
            return Event(self) == Event(other)
        elif type(other) is self.__class__:
            return (self._pre_continue == other._pre_continue
                    and self._post_continue == other._post_continue
                    and Event(self) == Event(other))
        return False

class TimeSlice(object):
    def __init__(self, span, slice_range):
        # The slice stores the unchanged events that overlap with the slice
        # (ie each Event may have start and end times outside of the slice).
        # These are sliced on-demand.
        if len(slice_range) != 2:
            raise ValueError('slice range must have 2 elements')
        self._slice_range = slice_range
        self._events = []
        for event in span:
            if event.in_span_range(slice_range):
                self._events.append(event)

    def sliced_events(self):
        '''
        Return the events contained within the slice, sliced to fit and marked
        if they are continuing an event before or after.
        '''
        for event in self._events:
            yield SlicedEvent(self._slice_range, event)
    
    def raw_events(self):
        '''
        Return the events contained within the slice, but otherwise unchanged.
        '''
        return self._events

    def slice_range(self):
        return self._slice_range

    def start(self):
        return self._slice_range[0]

    def end(self):
        return self._slice_range[1]

    def num_events(self):
        return len(self._events)

    def is_atomic_slice(self):
        '''
        returns whether a slice is atomic or not.
        a slice is atomic if, when subdivided into any number an arrangement
        of smaller slices, those subslices contain the exact same events
        contained by this slice.
        TODO: if we implement 'zero-duration' events like time signature
        markers, how does this work? 
        '''
        for event in self.sliced_events():
            event_start = event.time().in_beats()
            event_end = event.time().in_beats() + event.unwrap().duration().in_beats()
            if event_start > self.start() or event_end < self.end():
                return False
        return True