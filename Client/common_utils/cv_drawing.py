from Client.common_utils.constants import RBGColors
from Client.models.core import *

import cv2
import cv2 as cv
import numpy

fonts = {
    "default": {
        "font": cv2.FONT_HERSHEY_PLAIN,
        "scale": 1,
        "color": (0, 230, 0),
        "line type": 2,
        "thickness": 1
    }
}


def draw_line(image, pt1: Point, pt2: Point, color_override=RBGColors.BLUE):
    font = fonts["default"]
    color = color_override
    cv2.line(image, pt1.xy, pt2.xy, color, font["thickness"], 4)


def draw_line_and_distance(image, pt1: Point, pt2: Point, color_override=RBGColors.BLUE):
    font = fonts["default"]
    color = color_override
    middle_x = int(numpy.median([pt1.x, pt2.x]))
    middle_y = int(numpy.median([pt1.y, pt2.y]))
    dist = pt1.distance(pt2)
    cv2.line(image, pt1.xy, pt2.xy, color, font["thickness"], 4)
    write_label(image, Point(middle_x, middle_y), f"{dist}", color_override=RBGColors.GREEN)


def resize(image, scale: float):
    w, h = image.shape[1], image.shape[0]
    return cv.resize(image, (int(w * scale), int(h * scale)), interpolation=cv.INTER_AREA)


def write_label(base_img, point: Point, text: str, color_override=RBGColors.GREEN):
    font = fonts["default"]
    color = color_override
    return cv2.putText(base_img,
                       text,
                       (point.x, point.y - 5),
                       font["font"],
                       font["scale"],
                       color,
                       font["thickness"],
                       font["line type"]
                       )


def draw_circle(base_img, point: Point, label="", radius=5):
    font = fonts["default"]
    write_label(base_img, point, label)
    return cv.circle(base_img,
                     (point.x, point.y + radius),
                     radius,
                     font["color"],
                     font["thickness"], font["line type"]
                     )


def highlight_match(base_img, bbox: BBox, label_name, color_override=RBGColors.GREEN):
    font = fonts["default"]
    font["color"] = color_override
    cv.rectangle(base_img, bbox.top_left,
                 bbox.bottom_right, font["color"], 2)
    write_label(base_img, bbox.bottom_right, label_name)


def draw_contour_points(base_img, points: ContourPoints):
    cv2.circle(base_img, points.center.xy, 8, RBGColors.YELLOW, -1)
    """
    draw_line_and_distance(base_img,points.center, points.left)
    draw_line_and_distance(base_img,points.center, points.right)
    draw_line_and_distance(base_img,points.center, points.top)
    draw_line_and_distance(base_img,points.center, points.bottom)
    """
    cv2.circle(base_img, points.left.xy, 8, RBGColors.LIGHT_BLUE, -1)
    cv2.circle(base_img, points.right.xy, 8, RBGColors.DARK_BLUE, -1)
    cv2.circle(base_img, points.top.xy, 8, RBGColors.LIGHT_RED, -1)
    cv2.circle(base_img, points.bottom.xy, 8, RBGColors.DARK_RED, -1)

    draw_line_and_distance(base_img,points.center, Point(points.center.x, points.top.y), color_override=RBGColors.GRAY)
    draw_line_and_distance(base_img,points.center, Point(points.center.x, points.bottom.y), color_override=RBGColors.GRAY)
    draw_line_and_distance(base_img,points.center, Point(points.left.x, points.center.y), color_override=RBGColors.GRAY)
    draw_line_and_distance(base_img,points.center, Point(points.right.x, points.center.y), color_override=RBGColors.GRAY)
    cv2.circle(base_img, (points.left.x, points.center.y), 4, RBGColors.GRAY, -1)
    cv2.circle(base_img, (points.right.x, points.center.y), 4, RBGColors.GRAY, -1)
    cv2.circle(base_img, (points.center.x, points.top.y), 4, RBGColors.GRAY, -1)
    cv2.circle(base_img, (points.center.x, points.bottom.y), 4, RBGColors.GRAY, -1)

    write_label(base_img, points.top, points.name)


def draw_contour_parameter(base_img, cnt: ContourPoints):
    cv2.drawContours(base_img, [cnt.contours], 0, RBGColors.GREEN, 3)


def merge_images(im1, im2, merge_point: Point, im2_size: tuple):
    try:
        im1 = cv2.cvtColor(im1, cv2.COLOR_GRAY2RGB)
    except Exception as e:
        pass
    try:
        im2 = cv2.cvtColor(im2, cv2.COLOR_GRAY2RGB)
    except Exception as e:
        pass

    im2 = cv2.resize(im2, (im2_size[0], im2_size[1]),
                     interpolation=cv2.INTER_AREA)
    im1[merge_point.y:merge_point.y + im2_size[1],
        merge_point.x:merge_point.x + im2_size[0]] = im2
    return im1

