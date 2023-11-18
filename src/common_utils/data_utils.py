import cv2 as cv
import logging


logger = logging.getLogger(__name__)

fonts = {
    "default": {
        "font": cv.FONT_HERSHEY_PLAIN,
        "scale": .5,
        "color": (0, 230, 0),
        "line type": 2,
        "thickness": 1
    }
}
