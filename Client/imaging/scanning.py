import cv2, logging
import Client.common_utils.cv_drawing as drawing_utils 
from Client.data.bank import DataBank
from Client.common_utils.models import Event, ReactiveList, Point

logger = logging.getLogger(__name__)

from Client.models.core import BBox, Reference

tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
img_match_method = cv2.TM_SQDIFF_NORMED
section_offset = 25


class ImageScanner:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Creating new ImageScanner')
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        self.trackers: ReactiveList[Tracker] = ReactiveList()
        self.current_index = 0
        self.current_num_trackers = 0
        self._trackers_to_add = []
        self._trackers_to_remove = []
        self.data_bank = DataBank()

        # Events
        self.on_trackers_updated = Event()

    def rolling_scan(self):
        for tracker in self.trackers:
            if tracker.matched:
                # Has match, continue finding
                tracker.track()
            elif self.current_index == self.trackers.index(tracker):
                # No match scan only when it matches
                tracker.track()
        self.current_index += 1
        if self.current_index >= len(self.trackers):
            self.current_index = 0

        self._safely_update_trackers()

    def add_tracker(self, tracker):
        self._trackers_to_add.append(tracker)
        logger.debug(f"Adding Tracker to be added at end of cycle. {tracker.name}")

    def remove_tracker(self, tracker):
        self._trackers_to_remove.append(tracker)
        logger.debug(f"Adding Tracker to be removed at end of cycle. {tracker.name}")

    def get_scanner_by_name(self, name):
        for tracker in self.trackers:
            if tracker.name == name:
                return tracker
        return None

    def _safely_update_trackers(self):
        change = False
        for tracker in self._trackers_to_remove:
            change = True
            self.current_num_trackers -= 1
            if tracker in self.trackers:
                self.trackers.remove(tracker)
                logger.debug(f"Removing Tracker {tracker.name} from trackers")

        for tracker in self._trackers_to_add:
            change = True
            self.current_num_trackers += 1
            self.trackers.append(tracker)
            logger.debug(f"Adding Tracker {tracker.name} to trackers")
            logger.debug(f"Adding ImageProcess to processor")
            from Client.imaging.processing import ImageProcessor
            ImageProcessor().add_image_process(tracker.image_reference.image_process)

        self._trackers_to_add = []
        self._trackers_to_remove = []
        self.data_bank.update_debug_entry("# Trackers", str(len(self.trackers)))
        if change:
            self.on_trackers_updated()


class Tracker:
    sub_region = None

    def __init__(self, image_reference: Reference):
        self.name = image_reference.name
        self.box_points = ()
        self.last_position: Point = None
        self.bbox = None
        self.scan_bbox: BBox = None
        self.image_reference = image_reference
        self.match, self.match_val = None, 1
        self.matched = False

    def track(self):
        if self.image_reference.reference_type.name == 'hsv contour':
            ref_obj = self.image_reference
            im_proc = self.image_reference.image_process
            scan_image = self.image_reference.image_process.get_main_image()
            if self.set_scan_bbox():
                img_out = scan_image
                gpo_x = self.scan_bbox.x
                gpo_y = self.scan_bbox.y
                scan_image = scan_image[self.scan_bbox.y:self.scan_bbox.bottom_right.y,
                                        self.scan_bbox.x: self.scan_bbox.bottom_right.x]
                self.image_reference.image_process.images["sub image"] = scan_image
            else:
                gpo_x, gpo_y = 0, 0
                self.image_reference.image_process.images["sub image"] = None

            self.match, self.match_val = self.image_reference.find_match(im_proc.image_contours)
            if self.match is not None:
                self.matched = True
            else:
                self.matched = False

    def draw_match(self, output_image):
        if self.image_reference.reference_type.name == 'hsv contour':
            drawing_utils.draw_contour_parameter(output_image, self.match)
            drawing_utils.draw_contour_points(output_image, self.match)

    def set_scan_bbox(self) -> bool:
        return False
        if self.last_position is None:
            return False
        # logger.debug("scan bboxing")

        if self.image_reference.reference_type.name == 'hsv contour':
            rect = cv2.minAreaRect()
            self.bbox = self.image_reference.minBox
            n_bbox = BBox(None,
                          self.last_position.x - section_offset,
                          self.last_position.y - section_offset,
                          self.bbox.width + (section_offset * 2),
                          self.bbox.height + (section_offset * 2))

            img_h, img_w = self.image_reference.image_process.image.shape[:2]
            # Out of bounds checks
            # TL Check
            if n_bbox.y <= 1:
                if (n_bbox.y + section_offset) <= 1:
                    self.last_position = None
                    return False
                else:
                    n_bbox.y = n_bbox.y + section_offset
            else:
                n_bbox.y = n_bbox.y

            if n_bbox.x <= 1:
                if (n_bbox.x + section_offset) <= 1:
                    self.last_position = None
                    return False
                else:
                    n_bbox.x = n_bbox.x + section_offset
            else:
                n_bbox.x = n_bbox.x

            # BR Check
            if n_bbox.y + n_bbox.height >= img_h:
                if (n_bbox.y + n_bbox.height) - section_offset >= img_h:
                    self.last_position = None
                    return False
                else:
                    n_bbox.height = n_bbox.height - section_offset
            if n_bbox.x + n_bbox.width >= img_w:
                if (n_bbox.x + n_bbox.width) - section_offset >= img_w:
                    self.last_position = None
                    return False
                else:
                    n_bbox.width = n_bbox.width - section_offset
            self.scan_bbox = n_bbox
            # logger.debug(f"scan_bbox: {self.scan_bbox}")
            return True
        return False
