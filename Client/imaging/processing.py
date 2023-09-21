from Client.cact_utils import opencv_utils
from Client.data.bank import DataBank
import logging

from Client.models.core import Point
from Client.models.image_process import *

logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
class ImageProcessor:
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info('Creating new ImageProcessor')
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        logger.debug("Initializing ImageProcessor")
        # Base Config
        self.show_contours = True

        # Base properties
        self.video_read_height = 1920
        self.video_read_width = 1080
        self.output_width = 960
        self.output_height = 540
        self.secondary_image_size = (96 * 3, 54 * 3)
        self.secondary_image_point = Point(25, 25)

        # Base Video
        self.vid_cap = cv2.VideoCapture(0)
        self.vid_cap.set(3, self.video_read_width)
        self.vid_cap.set(4, self.video_read_height)

        # Other Var
        self.data_bank = DataBank()

        # Frames
        self.tracker_index = 0
        self.current_image_outputs: dict[str: ImageProcess] = {"main": None, "secondary": None}
        self.frames: dict[str: ImageProcess] = {}

        # Finalize Init
        self.init_images()

    # Processing Functions
    def process_images(self):
        self._process_images()

    def init_images(self):
        if "main output" not in self.frames:
            self.frames["main output"] = OutputImageProcess(None, "main output")
        if "main color" not in self.frames:
            self.frames["main color"] = ColorImageProcess(None, "main color")
        if "main grayscale" not in self.frames:
            self.frames["main grayscale"] = GrayImageProcess(None, "main grayscale")
        if "main threshold" not in self.frames:
            self.frames["main threshold"] = ThresholdImageProcess(None, "main threshold")
        if "main hsv":
            self.frames["main hsv"] = HSVImageProcess(None, "main hsv", show_contours=True)
        self.current_image_outputs["main"] = self.frames["main output"]

    def read_frame(self):
        ret, read_frame = self.vid_cap.read()
        if not ret:
            logger.critical("Can't receive frame (stream end?). Exiting application...")
            exit(0)

        read_frame = cv2.resize(read_frame, (self.output_width, self.output_height),
                                interpolation=cv2.INTER_AREA)
        return read_frame

    def _process_images(self):
        read_frame = self.read_frame()
        self.frames["main color"].process_image(image=read_frame)
        self.frames["main output"].process_image(image=self.frames["main color"].get_main_image())
        for name, im_proc in self.frames.items():
            if im_proc.process_type is not None:
                if im_proc.process_type == "threshold":
                    im_proc.process_image(image=self.frames["main grayscale"].get_main_image())
                elif im_proc.process_type == "hsv":
                    im_proc.process_image(hsv_image=self.frames["main color"].images["hsv"],
                                          output_image=self.frames["main output"].get_main_image())
                    if im_proc.show_contours:
                        im_proc.draw_contours(self.frames["main output"].get_main_image())
                elif im_proc.process_type == "grayscale":
                    im_proc.process_image(image=self.frames["main color"].images["bgr"])
            else:
                logger.warning(f"Failed to process image: {im_proc.name}. Type was None.")

    def set_output_image(self, output_name: str, secondary=False):
        op_name = "secondary" if secondary else "main"
        logger.debug(f"Setting {op_name} source to {output_name}")
        if output_name in self.frames:
            self.current_image_outputs[op_name] = self.frames[output_name]
        else:
            logger.warning("Failed to set output image. Setting to default [None]")
            self.current_image_outputs[op_name] = None

    def get_output_image(self, secondary=False):
        co = self.current_image_outputs["secondary"] if secondary else self.current_image_outputs["main"]
        if co is not None:
            try:
                # Is 2D?
                x, y = co.shape[::1]
                return cv2.cvtColor(co, cv2.COLOR_GRAY2RGBA)
            except Exception as e:
                pass
            # Is 3D
            return cv2.cvtColor(co, cv2.COLOR_BGR2RGBA)

    def get_combined_output_frame(self):
        if type(self.current_image_outputs["main"]) is OutputImageProcess:
            im1 = self.current_image_outputs["main"].get_processed_image()
        else:
            im1 = self.current_image_outputs["main"].get_main_image()

        if self.current_image_outputs.get("secondary") is None:
            return im1

        if type(self.current_image_outputs["secondary"]) is OutputImageProcess:
            im2 = self.current_image_outputs["secondary"].get_processed_image()
        else:
            im2 = self.current_image_outputs["secondary"].get_main_image()

        return opencv_utils.merge_images(
            im1,
            im2,
            self.secondary_image_point,
            self.secondary_image_size
        )

    def finalize_output(self):
        self.frames["main output"].finalize_processed_image()

    def add_image_process(self, im_proc: ImageProcess):
        self.frames[im_proc.name] = im_proc

    def remove_image_process(self, im_proc: ImageProcess):
        self.frames[im_proc.name] = None

    def get_image_process(self, name):
        return self.frames.get(name, None)
