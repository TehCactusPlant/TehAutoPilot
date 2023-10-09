import logging
import time

import numpy

logger = logging.getLogger(__name__)


class Event(object):
    def __init__(self):
        self._event_listeners = []

    def __iadd__(self, handler):
        self._event_listeners.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self._event_listeners:
            self._event_listeners.remove(handler)
            return self

    def __call__(self, *args, **kwargs):
        for listener in self._event_listeners:
            listener(*args, **kwargs)

    def __del__(self):
        logger.debug("Event Destroyed")


class PairedList(list):
    def __init__(self):
        super().__init__()
        self.on_entry_changed = Event()
        self.on_removed_item = Event()
        self.on_added_item = Event()

    def __setitem__(self, key, value):
        super(PairedList, self).__setitem__(key, value)
        self.on_entry_changed(value)

    def __delitem__(self, value):
        index = self.index(value)
        super(PairedList, self).__delitem__(value)
        self.on_removed_item(index)

    def __add__(self, value):
        super(PairedList, self).__add__(value)
        self.on_added_item(value)

    def __iadd__(self, value):
        super(PairedList, self).__iadd__(value)
        self.on_added_item(value)

    def append(self, value):
        super(PairedList, self).append(value)
        self.on_added_item(value)

    def remove(self, value):
        super(PairedList, self).remove(value)
        self.on_removed_item(value)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = (x, y)

    @staticmethod
    def from_tuple(tup):
        return Point(tup[0], tup[1])

    def distance(self, p2, precise=False):
        dst = numpy.sqrt(numpy.power((p2.x - self.x), 2) + numpy.power((p2.y - self.y), 2))
        if precise:
            return dst
        else:
            return int(dst)


class FPSCounter:
    def __init__(self):
        self.time1 = 0
        self.time2 = 1
        self.times = []
        self.avg_fps = 1
        self.last_fps = 1

    def get_fps(self):
        self.time2 = time.time()
        if self.time2 == self.time1:
            self.time1 -= .01
        self.last_fps = int(1.0 / (self.time2 - self.time1))
        self.times.append(self.last_fps)
        if len(self.times) > 60:
            self.times.pop(0)
        self.avg_fps = int(numpy.mean(self.times))
        self.time1 = self.time2
