import threading
import time
import cv2 as cv
import Client.database.core as db_con
from Client.models.core import *
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

ref_types = [
    "NODE",
    "MENU",
    "COMBAT"
]


def create_reference_image(base_img, location: Location):
    logger.info("Starting thread for reference image capture")
    thread = threading.Thread(target=_create_reference_image, args=(base_img,))
    thread.start()
    logger.info("Use mouse to drag and draw a square to crop a reference image.")
    logger.info("Press spacebar to confirm the image")


def create_new_node(base_img, location: Location):
    logger.info("Starting manual Node Creation")
    logger.info("Stand in position for node")
    thread = threading.Thread(target=_create_new_node, args=(base_img, location))
    thread.start()
    logger.info("Nodes requires a reference image. Starting create image reference.")


def get_nodes(location):
    pass


def get_locations():
    db = db_con.DBInterface()
    return db.get_locations()


def _create_new_node(base_img, location: Location, last_node=None):
    bbox, img_ref = _create_reference_image(base_img)
    player_x, player_y = base_img[::-1]
    player_x /= 2
    player_y /= 2
    x_off = player_x - bbox.top_left.x
    y_off = player_y - bbox.top_left.y
    db = db_con.DBInterface()
    logger.info("New node created")
    return db.create_node(location, img_ref, x_off, y_off)


def _create_reference_image(base_img):
    cv.imshow("GETREF", base_img)
    base_image_clone = base_img.copy()
    global ref_image
    complete = False
    cropped = None
    base_img = base_image_clone.copy()
    bbox = BBox.from_roi(cv.selectROI('GETREF', base_img))
    cropped = crop_image(base_img, bbox)
    ref_image = None
    while not complete:
        k = cv.waitKey(1)
        cv.imshow("GETREF", base_img)
        if cropped is not None:
            cv.imshow("Cropped", cropped)
            if k == 32:  # Press Space bar
                # Save image to location directory
                # Save details to DB
                complete = True
                logger.info("Reference image captured and saved. Ending img_ref creation")
                cv.destroyWindow("GETREF")
                cv.destroyWindow("Cropped")
                db = db_con.DBInterface()
                cv.destroyWindow('GETREF')
                cv.destroyWindow('Bot View')
                return bbox, db.create_img_ref(image=cropped)





def crop_image(image, bbox: BBox):
    return image[bbox.top_left.y:bbox.bottom_right.y, bbox.top_left.x, bbox.bottom_right.x]
