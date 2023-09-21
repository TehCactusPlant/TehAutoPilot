import logging
import time

import cv2, numpy
import Client.cact_utils.opencv_utils as cv_utils
from Client.data.bank import DataBank

from Client.models.core import ImageProcess, ContourPoints, FPSCounter

logger = logging.getLogger(__name__)

class OutputImageProcess(ImageProcess):
    def __init__(self, _id, name=None, args=None):
        super().__init__(_id, name, args)
        self.process_type = "output"
        self.data_bank = DataBank()
        self.fps_counter = FPSCounter()

    def process_image(self, **kwargs):
        if "main" in self.images:
            self.images["processed"] = self.images["main"]
            self.images["main"] = kwargs.get("image").copy()
        else:
            self.images["main"] = kwargs.get("image").copy()
            self.images["processed"] = self.images["main"]

    def get_processed_image(self):
        return self.images["processed"]

    def finalize_processed_image(self):
        self.fps_counter.get_fps()
        self.images["processed"] = self.images["main"]
        self.data_bank.update_debug_entry("process/sec", str(self.fps_counter.last_fps))
        self.data_bank.update_debug_entry("average proc/sec", self.fps_counter.avg_fps)


class ColorImageProcess(ImageProcess):
    def __init__(self, _id, name=None, args=None):
        super().__init__(_id, name, args)
        self.process_type = "color"

    def process_image(self, **kwargs):
        image = kwargs.get("image", None)
        if image is not None:
            self.images["bgr"] = image
            self.images["hsv"] = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            self.images["main"] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


class ThresholdImageProcess(ImageProcess):
    def __init__(self, _id, name=None, args=None):
        super().__init__(_id, name, args)
        self.process_type = "threshold"
        self.image_scale = 0.5
        self.thresh_max = 255
        self.adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        self.threshold_type = cv2.THRESH_BINARY
        self.blockSize = 13
        self.C = 4

    def process_image(self, **kwargs):
        image = kwargs.get("image", None)
        if image is not None:
            self.images["main"] = cv2.adaptiveThreshold(
                image,
                self.thresh_max,
                self.adaptive_method,
                self.threshold_type,
                self.blockSize,
                self.C)


class GrayImageProcess(ImageProcess):
    def __init__(self, _id, name=None, args=None):
        super().__init__(_id, name, args)
        self.process_type = "grayscale"

    def process_image(self, **kwargs):
        image = kwargs.get("image", None)
        if image is not None:
            self.images["main"] = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


class HSVImageProcess(ImageProcess):
    def __init__(self, _id, name=None, args=None, show_contours=False):
        super().__init__(_id, name, args)
        logger.debug("Initializing new HSV Image Process")
        self.process_type = "hsv"
        self.data_bank = DataBank()
        self.image_contours = None
        self.show_contours = show_contours

        if args is not None:
            self.min_hsv = [args.get_arg_value("h_min"), args.get_arg_value("s_min"),
                            args.get_arg_value("v_min")]
            self.max_hsv = [args.get_arg_value("h_max"), args.get_arg_value("s_max"),
                            args.get_arg_value("v_max")]
        else:
            self.set_hsv_range([0, 0, 0], [255, 255, 255])

    def set_hsv_range(self, h_min, h_max):
        logger.debug(f"{self.name} updated HSV values to {h_min} and {h_max}")
        self.min_hsv = numpy.array(h_min, numpy.uint8)
        self.max_hsv = numpy.array(h_max, numpy.uint8)

    def process_image(self, **kwargs):
        output_image = kwargs.get("output_image", None)
        hsv_image = kwargs.get("hsv_image", None)
        self.images["main"] = cv2.inRange(hsv_image, self.min_hsv, self.max_hsv)
        kernel = numpy.ones((2, 2), numpy.uint8)
        self.images["main"] = cv2.erode(self.images["main"], kernel, iterations=3)
        self.images["main"] = cv2.dilate(self.images["main"], kernel, iterations=5)
        if self.images.get("sub image") is not None:
            print("Scanning sub image")
            self.image_contours, test_hierarchy = cv2.findContours(
                self.images["sub image"], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            self.image_contours, test_hierarchy = cv2.findContours(self.images["main"], cv2.RETR_TREE,
                                                                   cv2.CHAIN_APPROX_SIMPLE)
        self.images["masked"] = cv2.bitwise_and(output_image, output_image, mask=self.images["main"])
        self.data_bank.update_debug_entry("show contours",self.show_contours)

    def draw_contours(self, output_frame):
        for i in range(0, len(self.image_contours)):
            c_points = ContourPoints(self.image_contours[i], f"g-{str(i)}")
            cv_utils.draw_contour_parameter(output_frame, c_points)
            cv_utils.write_label(output_frame, c_points.center, c_points.name)

    def label_contours(self, output_frame):
        for i in range(0, len(self.image_contours)):
            c_points = ContourPoints(self.image_contours[i], f"g-{str(i)}")
            cv_utils.write_label(output_frame, c_points.center, c_points.name)

    def update_show_contours(self, show: bool):
        self.show_contours = show