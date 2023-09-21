import collections
import time
from abc import abstractmethod

import cv2
import numpy

from Client.models.core_impl import *

ROOT_DB = ""
# Tuples
NodeLink = collections.namedtuple('NodeLink', ('node1', 'node2'))


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


class ContourPoints:
    def __init__(self, cnt, name=""):
        self.MAX_DISTANCE = 40
        M = cv2.moments(cnt)
        try:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        except Exception as e:
            cX = int(M["m10"] / .1)
            cY = int(M["m01"] / .1)
        self.contours = cnt
        self.center = Point(cX, cY)
        self.top = Point.from_tuple(tuple(cnt[cnt[:, :, 1].argmin()][0]))
        self.bottom = Point.from_tuple(tuple(cnt[cnt[:, :, 1].argmax()][0]))
        self.left = Point.from_tuple(tuple(cnt[cnt[:, :, 0].argmin()][0]))
        self.right = Point.from_tuple(tuple(cnt[cnt[:, :, 0].argmax()][0]))
        self.name = name
        self.top_distance = self.top.distance(self.center)
        self.bottom_distance = self.bottom.distance(self.center)
        self.left_distance = self.left.distance(self.center)
        self.right_distance = self.right.distance(self.center)

    def in_range(self, target_cnt):
        if numpy.abs(self.top_distance - target_cnt.top_distance) > self.MAX_DISTANCE:
            return False
        if numpy.abs(self.bottom_distance - target_cnt.bottom_distance) > self.MAX_DISTANCE:
            return False
        if numpy.abs(self.left_distance - target_cnt.left_distance) > self.MAX_DISTANCE:
            return False
        if numpy.abs(self.right_distance - target_cnt.right_distance) > self.MAX_DISTANCE:
            return False
        return True


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


class BBox(BBoxImpl):
    def __init__(self, _id, x=None, y=None, width=None, height=None):
        super().__init__(_id, x, y ,width, height)

    def bbox(self):
        return (self.x, self.y, self.width, self.height)

    @staticmethod
    def from_tuple(tup):
        print(tup)
        return BBox(None, tup[0], tup[1], tup[2], tup[3])


class Arg(ArgImpl):
    def __init__(self, _id, arg_name=None, arg_value=None):
        super().__init__(_id)

        if self.get_id() is not None:
            data = self.get()
            self.name = data[0]["arg_name"]
            self.value = data[0]["arg_value"]
        else:
            self.name = arg_name
            self.value = arg_value
            self.save()

    def update_value(self, new_value):
        self.value = str(new_value)


class ArgEntry(ArgEntryImpl):
    def __init__(self, _id, name=None):
        super().__init__(_id)
        self.args: list[Arg] = []
        if self.get_id() is not None:
            data = self.get()
            arg_data = self.get_all_args()
            logger.debug(f"Args obtained for arg_id {self.get_id()}:\n{arg_data}")
            self.name = data[0]["name"]
            self.args = [Arg(entry["arg"]) for entry in arg_data]
        else:
            self.args = []
            self.name = name
            self.save()

    def add_arg(self, arg):
        self.args.append(arg)

    def update_arg(self, arg_name, new_value, new_name=None):
        for arg in self.args:
            if arg.name == arg_name:
                if new_name is not None:
                    arg.name = new_name
                arg.update_value(new_value)
                arg.save()

    def get_arg_value(self, arg_name):
        for arg in self.args:
            if arg.name == arg_name:
                logger.debug(f"Value {arg.value} found for arg {arg.name}")
                return arg.value
        return None


class Location(LocationImpl):
    def __init__(self, _id, location_name=None):
        super().__init__(_id)
        if self.get_id() is None:
            self.location_name = location_name
        else:
            data = self.get()
            self.location_name = data[0]["location_name"]


class Node(NodeImpl):
    def __init__(self, _id, location, x_off, y_off, image):
        super().__init__(_id)
        self.location: Location = location
        self.reference = None
        self.x_off = x_off
        self.y_off = y_off
        self.connected_nodes: list[Node] = []
        self.position = (0, 0)

    def link(self, node):
        if node not in self.connected_nodes:
            self.connected_nodes.append(node)


class ImageProcess(ImageProcessImpl):
    def __init__(self, _id, name=None, args=None):
        super().__init__(_id)
        self.process_type = None
        self.images = {}
        if self.get_id() is None:
            self.name = name
            self.args = args
        else:
            resp = self.get()
            if len(resp) > 0:
                self.name = resp[0]["name"]
                self.args = ArgEntry(resp[0]["arg_entry"])

    def process_image(self, **kwargs):
        logger.warning(f"process image not implemented but being called for {self.name}")

    def get_main_image(self):
        return self.images.get("main", None)


class ReferenceType(ReferenceTypeImpl):
    def __init__(self, _id, name=None):
        super().__init__(_id)
        if name is not None:
            self.name = name
            data = self.get_by_name()
            if len(data) > 0:
                self.set_id(data[0]["_id"])
        elif self.get_id() is not None:
            data = self.get()
            self.name = data[0]["reference_type_name"]
        else:
            self.name = name


class Reference(ReferenceImpl):
    def __init__(self, _id, bbox=None, args=None, reference_type=None, image_process=None, name=None):
        super().__init__(_id)
        self.minBox = None
        if self.get_id() is not None:
            data = self.get()
            self.bbox: BBox = BBox(data[0]["bbox"]) if data[0]["bbox"] is not None else bbox
            self.args: ArgEntry = ArgEntry(data[0]["arg_entry"])
            self.reference_type: ReferenceType = ReferenceType(data[0]["reference_type"])
            self.image_process: ImageProcess = ImageProcess(data[0]["image_process"])
        else:
            self.bbox: BBox = bbox
            self.args: ArgEntry = args
            self.reference_type: ReferenceType = reference_type
            self.image_process: ImageProcess = image_process

    @abstractmethod
    def find_match(self, ref_object):
        raise NotImplemented
