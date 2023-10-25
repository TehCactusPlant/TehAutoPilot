import logging
import math
import time

import numpy

logger = logging.getLogger(__name__)


class Event(object):
    """
    Basic event processor/handler
    """
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


class ReactiveList(list):
    """
    List with Events for responding to change
    """
    def __init__(self):
        super().__init__()
        self.on_entry_changed = Event()
        self.on_removed_item = Event()
        self.on_added_item = Event()
        self.on_list_cleared = Event()

    def __setitem__(self, key, value):
        super(ReactiveList, self).__setitem__(key, value)
        self.on_entry_changed(value)
        return self

    def __delitem__(self, value):
        index = self.index(value)
        super(ReactiveList, self).__delitem__(value)
        self.on_removed_item(index)
        return self

    def __add__(self, value):
        super(ReactiveList, self).__add__(value)
        self.on_added_item(value)
        return self

    def __iadd__(self, value):
        super(ReactiveList, self).__iadd__(value)
        self.on_added_item(value)
        return self

    def append(self, value):
        super(ReactiveList, self).append(value)
        self.on_added_item(value)

    def remove(self, value):
        index = self.index(value)
        super(ReactiveList, self).remove(value)
        self.on_removed_item(index)

    def clear(self):
        super(ReactiveList, self).clear()
        self.on_list_cleared()

class SafetyList(list):
    def __init__(self):
        super().__init__()
        self.on_entry_changed = Event()
        self.on_removed_item = Event()
        self.on_added_item = Event()

        self.items_to_add = []
        self.items_to_remove = []
        self.items_to_update = {}

    def safely_update_list(self):
        for value in self.items_to_add:
            super(SafetyList, self).__add__(value)
            self.on_added_item(value)
        for value in self.items_to_remove:
            index = self.index(value)
            super(SafetyList, self).__delitem__(value)
            self.on_removed_item(index)
        for key, value in self.items_to_update.items():
            super(SafetyList, self).__setitem__(key, value)
            self.on_entry_changed(value)
        self.items_to_add = []
        self.items_to_remove = []
        self.items_to_update.clear()

    def __setitem__(self, key, value):
        self.items_to_update[key] = value

    def __delitem__(self, value):
        self.items_to_remove.append(value)

    def __add__(self, value):
        self.items_to_add.append(value)
        self.on_added_item(value)

    def __iadd__(self, value):
        self.items_to_add.append(value)
        self.on_added_item(value)

    def append(self, value):
        super(SafetyList, self).append(value)
        self.on_added_item(value)

    def remove(self, value):
        super(SafetyList, self).remove(value)
        self.on_removed_item(value)


class ReactiveStore:
    """
    Object for thread safe manipulation of singleton dictionary
    in multithread environment

    Includes event on_store_change for responding to change
    """
    def __init__(self):
        self._data_store = {}
        self.thread_safe_changes = {}

        # Events
        self.on_store_change = Event()

    def get_variable_value(self, name):
        return self._data_store.get(name)

    def get_all(self):
        """
        Safely returns a copy of the list to be iterated through
        """
        return self._data_store.copy()

    def update_variable(self, key, value):
        """
        Update variable instantly. Not thread safe.

        key = dictionary key for entry to be updated
        value = new value to be updated
        """
        self._data_store[key] = value
        self.on_store_change(key, value)

    def thread_safe_update_variable(self, key, value):
        """
        Thread Safe updates to dictionary

        key = dictionary key for entry to be updated
        value = new value to be updated
        """
        self.thread_safe_changes[key] = value

    def thread_safe_update(self):
        for key, value in self.thread_safe_changes.items():
            self._data_store[key] = value
            self.on_store_change(key, value)
        self.thread_safe_changes.clear()


class Point:
    """
    Point in Space

    X = X pos
    Y = Y Pos
    xy = Tuple of xy coordinates
    """
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

    def angle(self, target):
        delta_x = target.x - self.x
        delta_y = target.y - self.y
        rad = math.atan2(delta_y, delta_x)
        print(rad)
        return rad


class Vector:
    def __init__(self, direction, magnitude):
        self.direction = direction
        self.magnitude = magnitude

    @classmethod
    def from_points(cls, start: Point, destination: Point):
        mag = Vector.get_distance(start, destination)
        dir = Vector.get_direction(start, destination)
        return cls(dir, mag)

    @staticmethod
    def get_distance(start, destination: Point, precise=True):
        dst = numpy.sqrt(numpy.power((destination.x - start.x), 2) + numpy.power((destination.y - start.y), 2))
        if precise:
            return dst
        else:
            return int(dst)

    @staticmethod
    def get_direction(start, destination):
        delta_x = destination.x - start.x
        delta_y = destination.y - start.y
        rad = math.atan2(delta_y, delta_x)
        return rad

    def get_terminal_point(self, start_point: Point):
        dest_x = int(start_point.x + self.magnitude * numpy.cos(self.direction))
        dest_y = int(start_point.y + self.magnitude * numpy.sin(self.direction))
        return Point(dest_x, dest_y)


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
