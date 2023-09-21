import math
import threading
import time
from enum import Enum
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


class Colors:
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 244)
    LIGHT_BLUE = (255, 140, 127)
    DARK_BLUE = (154, 15, 0)
    LIGHT_RED = (60, 60, 255)
    DARK_RED = (0, 0, 122)


def draw_line(image, pt1: Point, pt2: Point, color_override=Colors.BLUE):
    font = fonts["default"]
    color = (255, 0, 0)
    cv2.line(image, pt1, pt2, color, font["thickness"], 4)


def draw_line_and_distance(image, pt1: Point, pt2: Point, color_override=Colors.BLUE):
    font = fonts["default"]
    color = (255, 0, 0)
    middle_x = int(numpy.median([pt1.x, pt2.x]))
    middle_y = int(numpy.median([pt1.y, pt2.y]))
    dist = pt1.distance(pt2)
    cv2.line(image, pt1.xy, pt2.xy, color, font["thickness"], 4)
    write_label(image, Point(middle_x, middle_y), f"{dist}", color_override=Colors.GREEN)


def resize(image, scale: float):
    w, h = image.shape[1], image.shape[0]
    return cv.resize(image, (int(w * scale), int(h * scale)), interpolation=cv.INTER_AREA)


def write_label(base_img, point: Point, text: str, color_override=Colors.GREEN):
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


def highlight_match(base_img, bbox: BBox, label_name, color_override=Colors.GREEN):
    font = fonts["default"]
    font["color"] = color_override
    cv.rectangle(base_img, bbox.top_left,
                 bbox.bottom_right, font["color"], 2)
    write_label(base_img, bbox.bottom_right, label_name)


def draw_contour_points(base_img, points: ContourPoints):
    draw_line_and_distance(base_img,points.center, points.left)
    draw_line_and_distance(base_img,points.center, points.right)
    draw_line_and_distance(base_img,points.center, points.top)
    draw_line_and_distance(base_img,points.center, points.bottom)
    cv2.circle(base_img, points.left.xy, 8, Colors.LIGHT_BLUE, -1)
    cv2.circle(base_img, points.right.xy, 8, Colors.DARK_BLUE, -1)
    cv2.circle(base_img, points.top.xy, 8, Colors.LIGHT_RED, -1)
    cv2.circle(base_img, points.bottom.xy, 8, Colors.DARK_RED, -1)
    cv2.circle(base_img, points.center.xy, 8, Colors.YELLOW, -1)
    write_label(base_img, points.top, points.name)


def draw_contour_parameter(base_img, cnt: ContourPoints):
    cv2.drawContours(base_img, [cnt.contours], 0, Colors.GREEN, 3)


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

