import collections
from abc import abstractmethod

import cv2
import numpy

from Client.common_utils.models import Point, Vector, Event
from Client.data.bank import DataBank
from Client.models.core_impl import *

ROOT_DB = ""


class ContourPoints:
    def __init__(self, cnt, name=""):
        self.MAX_DISTANCE = 40
        self.MAX_PIXEL_DISTANCE = 15
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
        if numpy.abs(self.top_distance - target_cnt.top_distance) > self.MAX_DISTANCE or \
                numpy.abs(numpy.abs(target_cnt.top.y - target_cnt.center.y) - numpy.abs(self.top.y - self.center.y)) \
                >= self.MAX_PIXEL_DISTANCE:
            return False
        if numpy.abs(self.bottom_distance - target_cnt.bottom_distance) > self.MAX_DISTANCE or \
                numpy.abs(numpy.abs(target_cnt.bottom.y - target_cnt.center.y) - numpy.abs(self.bottom.y - self.center.y)) \
                >= self.MAX_PIXEL_DISTANCE:
            return False
        if numpy.abs(self.left_distance - target_cnt.left_distance) > self.MAX_DISTANCE or \
                numpy.abs(numpy.abs(target_cnt.center.x - target_cnt.left.x) - numpy.abs(self.center.x - self.left.x)) \
                >= self.MAX_PIXEL_DISTANCE:
            return False
        if numpy.abs(self.right_distance - target_cnt.right_distance) > self.MAX_DISTANCE or \
                numpy.abs(numpy.abs(target_cnt.center.x - target_cnt.right.x) - numpy.abs(self.center.x - self.right.x)) \
                >= self.MAX_PIXEL_DISTANCE:
            return False
        return True


class BBox(BBoxImpl):
    def __init__(self, _id, x=None, y=None, width=None, height=None):
        super().__init__(_id, x, y, width, height)

    def bbox(self):
        return (self.x, self.y, self.width, self.height)

    @staticmethod
    def from_tuple(tup):
        # logger.debug(tup)
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
    def __init__(self, _id, location, x_off, y_off, reference):
        super().__init__(_id)
        self.location: Location = location
        self.reference = reference
        self.x_off = x_off
        self.y_off = y_off
        self.node_links: list[NodeLink] = []
        self.position = Point(0, 0)
        self.is_drawn = False
        self.position_match = False

    def link(self, node_link):
        if node_link not in self.node_links:
            self.node_links.append(node_link)

    def update_position(self):
        if self.reference.match is not None:
            ref_loc = self.reference.match.center
            self.position = Point(ref_loc.x + self.x_off, ref_loc.y + self.y_off)
        else:
            # Handle Assumed position
            pass


class NodeLink(NodeLinkImpl):
    def __init__(self, _id, node1, node2, distance, direction):
        super().__init__(_id)
        self.node1: Node = node1
        self.node2: Node = node2
        self.dir_vector = Vector(direction, distance)
        self.link_nodes()

    def link_nodes(self):
        self.node1.link(self)
        self.node2.link(self)

    def get_other_node(self, node):
        conn_node = self.node1 if self.node2 == node else self.node2
        return conn_node


class ImageProcess(ImageProcessImpl):
    def __init__(self, _id, name=None, args=None):
        logger.debug(f"Initializing new ImageProcess")
        super().__init__(_id)
        self.process_type = None
        self.images = {}
        if self.get_id() is None:
            logger.debug(f"No ID found for new ImageProcess. given name = {name} Is this a new Process?")
            self.name = name
            self.args = args
        else:
            resp = self.get()
            if len(resp) > 0:
                self.name = resp[0]["name"]
                self.args = ArgEntry(resp[0]["arg_entry"])
                logger.debug(f"Created im_proc {self.name}. ID: {self.get_id()}")

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


class ReferenceBuilder:
    def __init__(self):
        self.data_bank = DataBank()

    @staticmethod
    def assemble_by_type(ref_type_id):
        c_type = None
        logger.debug(f"Assembling reference from builder with ID: {ref_type_id}")
        for t in DataBank().ref_types.get_all().values():
            if t.get_id() == ref_type_id:
                c_type = t
                break

        if c_type is None:
            return None
        elif c_type.name == "hsv contour":
            from Client.models.matching import ContourReference
            return ContourReference
        elif c_type.name == "text":
            pass
        return None


class Reference(ReferenceImpl):
    def __init__(self, _id, bbox=None, args=None, reference_type=None,
                 image_process=None, reference_data=None, name=None):
        super().__init__(_id)
        self.minBox = None
        if self.get_id() is not None:
            data = self.get()
            self.bbox: BBox = BBox(data[0]["bbox"]) if data[0]["bbox"] is not None else bbox
            self.args: ArgEntry = ArgEntry(data[0]["arg_entry"])
            self.reference_type: ReferenceType = ReferenceType(data[0]["reference_type"])
            if self.reference_type.name == "hsv contour":
                from Client.models.image_process import HSVImageProcess
                logger.debug(f"im_proc ID for create in ReferenceImpl({self.get_id()}): {data[0]['image_process']}")
                self.image_process: ImageProcess = HSVImageProcess(data[0]["image_process"])
            else:
                logger.error(f"Reference type: {self.reference_type.name} DOES NOT EXIST in Reference init switch")

            self.name = data[0]["name"]
        else:
            self.bbox: BBox = bbox
            self.args: ArgEntry = args
            self.reference_type: ReferenceType = reference_type
            self.image_process: ImageProcess = image_process
            self.reference_data = reference_data
            self.name = name

    @staticmethod
    def assemble_by_type(type):
        pass

    @abstractmethod
    def find_match(self, ref_object):
        raise NotImplemented

