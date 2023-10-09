import cv2

from Client.common_utils import cv_drawing
from Client.models.core import Reference, ContourPoints, BBox
from Client.common_utils.models import Point


class ContourReference(Reference):

    def __init__(self, _id, bbox=None, args=None, reference_type=None,
                 image_process=None, reference_data = None, name = None):
        super().__init__(_id, bbox, args, reference_type, image_process, reference_data, name)
        self.file_folder = "contours"
        if self.name is None:
            self.name = f"ip-{self.image_process.name}"
        if self.get_id() is not None:
            self.reference_data = self.load_numpy(f"{self.get_id()}_{self.name}")
        self.contour_points = ContourPoints(self.reference_data, self.name)
        self.THRESH = .10
        self.match_method = cv2.CONTOURS_MATCH_I1
        self.match = None

    def find_match(self, contour_to_search):
        if self.contour_points is None:
            return None, 99
        if contour_to_search is None:
            return None, 99
        max_match = 1
        matches = []
        pos = Point(0, 0)
        for contours in contour_to_search:
            cnt_point_dynamic = ContourPoints(contours, self.name)
            if self.contour_points.in_range(cnt_point_dynamic):
                ret = cv2.matchShapes(self.contour_points.contours, cnt_point_dynamic.contours, self.match_method, 0.0)
                if ret <= self.THRESH and ret <= max_match:
                    x, y, _, _ = cv2.boundingRect(cnt_point_dynamic.contours)
                    pos = Point(x, y)
                    if max_match > ret:
                        max_match = ret
                        matches = [cnt_point_dynamic]
            if len(matches) > 0:
                x,y,w,h = cv2.boundingRect(self.contour_points.contours)
                self.minBox = BBox(None, x,y,w,h)
                return matches[0], max_match
        self.minBox = None
        return None, 1

    def draw_match(self, output_image):
        if self.reference_type == 'hsv contour':
            opencv_utils.draw_contour_parameter(output_image, self.match)
            opencv_utils.draw_contour_points(output_image, self.match)
            opencv_utils.write_label(output_image, self.match.center, f"{self.match.name} %.5f" % self.match_val)

