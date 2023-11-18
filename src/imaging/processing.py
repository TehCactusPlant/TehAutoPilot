from src.common_utils.models import Event, Point
from src.models.image_process import *
import logging
import src.common_utils.cv_drawing as drawing_utils

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

        # Monitored Flags
        self.special_output = False
        self.special_output_open = False

        # Base Video
        self.vid_cap = cv2.VideoCapture(0)
        self.vid_cap.set(3, self.video_read_width)
        self.vid_cap.set(4, self.video_read_height)

        # Other Var
        self.data_bank = DataBank()
        self._im_proc_to_add = []
        self._im_proc_to_remove = []

        # Frames
        self.tracker_index = 0
        self.current_image_outputs: dict[str: ImageProcess] = {"main": None, "secondary": None}
        self.frames: dict[str: ImageProcess] = {}

        # Events
        self.on_process_images = Event()
        self.on_change_image_output = Event()
        self.on_update_image_processes = Event()

        # Finalize Init
        self.init_images()
        self._safely_update_image_processes()
        self.current_image_outputs["main"] = self.frames.get("main output")

    # Processing Functions
    def process_images(self):
        self._safely_update_image_processes()
        self._process_images()
        self.on_process_images()
        self.run_special_output()

    def toggle_run_special(self, state: bool):
        self.special_output = state

    def run_special_output(self):
        if self.special_output:
            k = cv2.waitKey(1)
            self.special_output_open = True
            output = cv2.resize(self.frames["main output"].get_processed_image(), (1600,900), interpolation=cv2.INTER_AREA)
            output = cv2.cvtColor(output, cv2.COLOR_RGB2BGRA)
            cv2.imshow('main view', output)
        else:
            if self.special_output_open:
                self.special_output_open = False
                cv2.destroyWindow('main view')

    def init_images(self):
        if "main output" not in self.frames:
            self.add_image_process(OutputImageProcess(None, "main output"))
        if "main color" not in self.frames:
            self.add_image_process(ColorImageProcess(None, "main color"))
        if "main grayscale" not in self.frames:
            self.add_image_process(GrayImageProcess(None, "main grayscale"))
        if "main threshold" not in self.frames:
            self.add_image_process(ThresholdImageProcess(None, "main threshold"))
        if "main hsv":
            self.add_image_process(HSVImageProcess(None, "main hsv", show_contours=False))

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
        for im_proc in self.frames.values():
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

    def change_image_output(self, output_name: str, secondary=False):
        op_name = "secondary" if secondary else "main"
        logger.debug(f"Setting {op_name} source to {output_name}")
        if output_name in self.frames:
            self.current_image_outputs[op_name] = self.frames[output_name]
        else:
            if op_name == "main":
                logger.warning("Failed to set main output image. Setting to default [main output]")
                self.current_image_outputs[op_name] = self.frames.get("main output")
            else:
                logger.warning("Failed to set secondary output image. Setting to default [None]")
                self.current_image_outputs[op_name] = None
        self.on_change_image_output()

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

        return drawing_utils.merge_images(
            im1,
            im2,
            self.secondary_image_point,
            self.secondary_image_size
        )

    def finalize_output(self):
        self.frames["main output"].finalize_processed_image()

    def add_image_process(self, im_proc: ImageProcess):
        self._im_proc_to_add.append(im_proc)

    def remove_image_process(self, im_proc: ImageProcess):
        self._im_proc_to_remove.append(im_proc)

    def get_image_process(self, name):
        return self.frames.get(name, None)

    def _safely_update_image_processes(self):
        change = False
        for im_proc in self._im_proc_to_remove:
            if self.frames.get(im_proc.name) is not None:
                change = True
                if self.current_image_outputs["main"] == im_proc:
                    self.change_image_output("main output")
                if self.current_image_outputs["secondary"] == im_proc:
                    self.change_image_output("None", secondary=True)
                self.frames[im_proc.name] = None
                self.frames.pop(im_proc.name)
                logger.debug(f"Removing image process {im_proc.name} to image processor")
        for im_proc in self._im_proc_to_add:
            logger.debug(f"Adding Improc {im_proc.name}")
            change = True
            self.frames[im_proc.name] = im_proc
            # self.change_image_output(im_proc.name, secondary=True)
            logger.debug(f"Adding image process {im_proc} to image processor")
        self._im_proc_to_add = []
        self._im_proc_to_remove = []
        if change:
            self.on_update_image_processes()

    def get_output_names(self):
        return {"main": self.current_image_outputs["main"].name,
                "secondary": "None" if self.current_image_outputs.get("secondary") is None else
                self.current_image_outputs["secondary"].name
                }
