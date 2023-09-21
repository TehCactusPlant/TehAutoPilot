import math
import logging
import cv2
import numpy as np
import cv2 as cv
import time

logger = logging.getLogger(__name__)
cap = cv.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)
pr_time = 0
end_time = 0
start_tick = 0
logger.info(f"CV2 Optimized: {cv.useOptimized()}")
font = cv2.FONT_HERSHEY_SIMPLEX
fontscale = .5
fontcolor = (0, 0, 0)
thickness = 2
linetype = 2
found_objs = {}
fonts = {
    "default": {
        "font" : cv2.FONT_HERSHEY_SIMPLEX,
        "scale" : .5,
        "color": (0, 255, 0),
        "line type": 2,
        "thickness": 1
    }
}

class Searchable:
    def __init__(self, tmp, name):
        self.name = name
        self.tmp = tmp
        self.w, self.h = tmp.shape[::-1]
        self.current_sect = 0
        self.max_sect = 9
        self.last_loc = None
        self.threshold = 0.3
        self.match_points = []
        self.has_match = False
        self.shape_color = (0,0,255)
        self.font = fonts["default"]

    def find_tmp(self, image):
        w, h = image.shape[::-1]
        partial_image = None
        sector_size = (int(w/3), int(h/3))
        x_off = 0
        y_off = 0
        if self.last_loc is None:
            x_off = int(sector_size[0] * (self.current_sect % 3))
            y_off = int(sector_size[1] * int((self.current_sect / 3)))
            self.update_sect()
        else:
            x_off = self.last_loc[0] - 100
            x_off = x_off if x_off >= 0 else 0
            y_off = self.last_loc[1] - 100
            y_off = y_off if y_off >= 0 else 0
        partial_image = image[
                        y_off: y_off + sector_size[1],
                        x_off: x_off + sector_size[0]
                        ]
        # print(f"img: {image.shape} - tmp: {self.tmp.shape} x_off {x_off} - y_off {y_off}")
        # Debug draw for scan
        cv.rectangle(thresh,
                     (x_off, y_off),
                     (x_off + partial_image.shape[1],
                      y_off + partial_image.shape[0]),
                     (0, 0, 255),
                     2)
        pts = np.where(res >= self.threshold)
        self.match_points = pts

    def update_sect(self):
        self.current_sect = self.current_sect + 1
        if self.current_sect >= self.max_sect:
            self.current_sect = 0

    def draw_match(self, image):
        self.has_match = False
        for pt in zip(*self.match_points[::-1]):
            cv.rectangle(image, pt, (pt[0] + self.w, pt[1] + self.h), self.font["color"], 2)
            cv.putText(
                image, self.name,
                (pt[0], pt[1] - 6),
                self.font["font"],
                self.font["scale"],
                self.font["color"],
                self.font["thickness"],
                self.font["line type"]
            )
            self.last_loc = pt
        logger.info(self.has_match)
        return image


oldman_r = Searchable(cv.imread("C:\\Users\\Cactus\\Pictures\\oldmanright.png", cv.IMREAD_GRAYSCALE), "egg man")
oldman_r_gray = Searchable(cv.imread("C:\\Users\\Cactus\\Pictures\\oldmanrightgray.png", cv.IMREAD_GRAYSCALE), "egg man")
oldman_r_color = Searchable(cv.imread("C:\\Users\\Cactus\\Pictures\\oldmanrightcolor.png", cv.IMREAD_GRAYSCALE), "egg man")



def render_fps(img):
    r_time = time.time()
    f_rate = 1.0 / (r_time - pr_time)
    bl = (10, 20)
    return cv2.putText(img, f"FPS: {str(math.floor(f_rate))}",
                bl,
                font,
                fontscale,
                fontcolor,
                thickness,
                linetype)


if not cap.isOpened():
    logger.error("Cannot open camera")
    exit()


debug_overlays = {"fps": render_fps}


def render_output(base_img, name="frame"):
    f_img = base_img
    for k, v in debug_overlays.items():
        f_img = v(base_img)
    cv.imshow(name, f_img)


def label_cell(image, name):
    h = image.shape[0]
    w = image.shape[1]
    bl = (int(10), int(h - 10))
    return cv2.putText(image,
                       str(name),
                       bl,
                       font,
                       fontscale,
                       fontcolor,
                       thickness,
                       linetype)


def shrink(image, scale):
    w, h = image.shape[::-1]
    return cv.resize(image, (int(w / scale), int(h / scale)), interpolation=cv.INTER_AREA)


def find_match(image, tmp):
    res = cv.matchTemplate(image, tmp, cv.TM_CCOEFF_NORMED)
    w, h = tmp.shape[::-1]
    loc = np.where(res >= 0.3)
    for pt in zip(*loc[::-1]):
        cv.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)


def render_multiple_outputs(images: dict):
    size = len(images)
    scale = int((size / 2) + 1)
    rows = []
    row = []
    for name, img in images.items():
        img = shrink(img, scale)
        img = label_cell(img, name)
        row.append(img)
        if len(row) == scale - 1:
            rows.append(row)
            row = []
    f_rows = []
    for row in rows:
        f_rows.append(np.hstack(tuple(row)))

    render_output(np.vstack(tuple(f_rows)))


while True:
    scale = 2
    # Capture frame-by-frame
    ret, frame = cap.read()
    images = {}

    # if frame is read correctly ret is True
    if not ret:
        logger.critical("Can't receive frame (stream end?). Exiting application...")
        break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    gray = cv.resize(gray, (int(1920 / scale), int(1080 / scale)), interpolation=cv.INTER_AREA)
    images["greyscale"] = gray
    # Display the resulting frame
    thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv.THRESH_BINARY, 11, 4)
    images["threshold"] = thresh
    # images["median"] = cv.medianBlur(thresh, 5)
    # images["blur"] = cv.bilateralFilter(thresh, 9, 75, 75)
    images["canny"] = cv.Canny(gray, 25, 80)

    orb = cv.ORB.create()

    side_by_side = {
        "thresh-gaus": thresh,
        "thresh-mean": thresh2
    }
    render_output(images["canny"])
    # render_multiple_outputs(side_by_side)

    pr_time = time.time()
    pr_tick = cv.getTickCount()
    if cv.waitKey(1) == ord('q'):
        break

    # When everything done, release the capture
cap.release()
cv.destroyAllWindows()