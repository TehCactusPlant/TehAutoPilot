import tkinter, colorsys, logging, numpy
from tkinter import ttk

from PIL import Image, ImageTk

import Client.common_utils.constants as util_consts
import Client.common_utils.cv_drawing as drawing_utils
from Client.imaging.processing import ImageProcessor
from Client.imaging.scanning import ImageScanner, Tracker
from Client.models.core import ImageProcess, Arg, ReferenceType, ArgEntry
from Client.common_utils.models import Event, Point
from Client.models.image_process import HSVImageProcess
from Client.models.matching import ContourReference
from Client.ui.widgets.custom_elements import Table
from Client.ui.widgets.sub_panels.sub_panel import SubPanel

logger = logging.getLogger(__name__)


class ImageProcessHSVAdjuster(SubPanel):
    def __init__(self, parent, im_proc: HSVImageProcess):
        # Base init
        super().__init__(parent)
        self.image_scanner = ImageScanner()

        # color blocks
        self._blank_img = numpy.ones(shape=[25, 25, 3], dtype=numpy.uint8)
        self.min_img = tkinter.Label(self, width=25, height=25)
        self.max_img = tkinter.Label(self, width=25, height=25)
        self.min_hsv_img = self._blank_img
        self.max_hsv_img = self._blank_img

        # Variables
        self.image_process = im_proc
        self.current_contours = {}
        self.test_tracker: Tracker = None
        self.color_range_presets: dict[str:ImageProcess] = ImageProcess.get_all()
        self.color_range_preset_names = []

        # TK Variables
        self.show_contours_flag = tkinter.IntVar()
        self.preset_name_var = None

        # Labels
        self.h_label = tkinter.Label(self, text="H")
        self.s_label = tkinter.Label(self, text="S")
        self.v_label = tkinter.Label(self, text="V")
        self.hsv_min_label = tkinter.Label(self, text="Min")
        self.hsv_max_label = tkinter.Label(self, text="Max")
        self.load_color_range_preset_label = tkinter.Label(self, text="Load Preset: ")

        # Sliders
        self.show_contours_toggle = tkinter.Checkbutton(
            self, text="Show Contours",
            variable=self.show_contours_flag, onvalue=1, offvalue=0, command=self.update_show_contours)

        self.min_h_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_h_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.min_s_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_s_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.min_v_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_v_slider = tkinter.Scale(self, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)

        # Buttons
        self.save_im_proc_btn = tkinter.Button(self, text="Save new Preset",
                                               command=self.save_hsv_image_process)

        # Positioning
        self.load_color_range_preset_label.grid(row=0, column=0)
        self.show_contours_toggle.grid(row=1, column=0)
        self.h_label.grid(row=2, column=0)
        self.s_label.grid(row=3, column=0)
        self.v_label.grid(row=4, column=0)
        self.hsv_min_label.grid(row=1, column=1)
        self.hsv_max_label.grid(row=1, column=2)
        self.min_h_slider.grid(row=2, column=1)
        self.max_h_slider.grid(row=2, column=2)
        self.min_s_slider.grid(row=3, column=1)
        self.max_s_slider.grid(row=3, column=2)
        self.min_v_slider.grid(row=4, column=1)
        self.max_v_slider.grid(row=4, column=2)
        self.save_im_proc_btn.grid(row=5, column=0, columnspan=3, sticky='ew')
        self.min_img.grid(row=6, column=1)
        self.max_img.grid(row=6, column=2)

        # Events
        self.on_save_hsv_image_process = Event()

        # Finalize init
        self.update_hsv(None)

    def set_slider_values_hex(self, _min, _max):
        self.min_h_slider.set(str(_min[0] / 255))
        self.min_s_slider.set(str(_min[1] / 255))
        self.min_v_slider.set(str(_min[2] / 255))
        self.max_h_slider.set(str(_max[0] / 255))
        self.max_s_slider.set(str(_max[1] / 255))
        self.max_v_slider.set(str(_max[2] / 255))

    def update_hsv(self, event):
        _min = numpy.array([self.min_h_slider.get(),
                            self.min_s_slider.get(),
                            self.min_v_slider.get()])
        _max = numpy.array([self.max_h_slider.get(),
                            self.max_s_slider.get(),
                            self.max_v_slider.get()])
        int_hsv_min = _min * 255
        int_hsv_max = _max * 255
        mn_h, mn_s, mn_v = _min
        mx_h, mx_s, mx_v = _max
        rgb_min = numpy.array(colorsys.hsv_to_rgb(mn_h, mn_s, mn_v)) * 255
        rgb_max = numpy.array(colorsys.hsv_to_rgb(mx_h, mx_s, mx_v)) * 255
        im = self._blank_img * rgb_min
        im = ImageTk.PhotoImage(image=Image.fromarray(im.astype(numpy.uint8)))
        self.min_img.configure(image=im)
        self.min_hsv_img = im

        im = self._blank_img * rgb_max
        im = ImageTk.PhotoImage(image=Image.fromarray(im.astype(numpy.uint8)))
        self.max_img.configure(image=im)
        self.max_hsv_img = im
        self.image_process.set_hsv_range(int_hsv_min, int_hsv_max)

    def save_hsv_image_process(self):
        if self.preset_name_var is not None:
            preset_name = self.preset_name_var.get()
            if preset_name == "" or preset_name == "<new>":
                logger.warning(f"Preset name is blank or <new>. Preset cannot be saved.")
        else:
            logger.warning(f"Preset name is None. Preset cannot be saved.")
            return
        _min = numpy.array([self.min_h_slider.get(),
                            self.min_s_slider.get(),
                            self.min_v_slider.get()])
        _max = numpy.array([self.max_h_slider.get(),
                            self.max_s_slider.get(),
                            self.max_v_slider.get()])

        int_hsv_min = _min * 255
        int_hsv_max = _max * 255
        if self.image_process.args is not None:
            im_proc: ImageProcess = self.color_range_presets[preset_name]
            im_proc.args.update_arg("h_min", int(int_hsv_min[0]))
            im_proc.args.update_arg("s_min", int(int_hsv_min[1]))
            im_proc.args.update_arg("v_min", int(int_hsv_min[2]))
            im_proc.args.update_arg("h_max", int(int_hsv_max[0]))
            im_proc.args.update_arg("s_max", int(int_hsv_max[1]))
            im_proc.args.update_arg("v_max", int(int_hsv_max[2]))
        else:
            im_proc: ImageProcess = HSVImageProcess(None, preset_name, None)
            im_proc.args = ArgEntry(None, im_proc.name)
            im_proc.args.add_arg(Arg(None, "h_min", int(int_hsv_min[0])))
            im_proc.args.add_arg(Arg(None, "s_min", int(int_hsv_min[1])))
            im_proc.args.add_arg(Arg(None, "v_min", int(int_hsv_min[2])))
            im_proc.args.add_arg(Arg(None, "h_max", int(int_hsv_max[0])))
            im_proc.args.add_arg(Arg(None, "s_max", int(int_hsv_max[1])))
            im_proc.args.add_arg(Arg(None, "v_max", int(int_hsv_max[2])))

        im_proc.save()
        self.color_range_presets[preset_name] = im_proc
        self.on_save_hsv_image_process()

    def update_show_contours(self, value=None):
        if value is None:
            value = self.show_contours_flag.get()
        else:
            self.show_contours_flag.set(value)
        show_conts = True if value == 1 else False
        self.image_process.update_show_contours(show_conts)


class ContourMatchingPanel(SubPanel):
    def __init__(self, parent, image_process: HSVImageProcess):
        # Base Init
        super().__init__(parent)
        self.image_scanner = ImageScanner()
        self.image_processor = ImageProcessor()

        # Variables
        self.image_process = image_process
        self.current_contours = {}
        self.current_contour = None
        self.test_tracker: Tracker = None
        self.image_process_for_save: HSVImageProcess = None
        self.reference_for_save: ContourReference = None

        # TK Variables
        self.matchable_contour_cbox_var = tkinter.StringVar()
        self.load_contour_cbox_name_var = tkinter.StringVar()

        # Labels
        self.panel_label = tkinter.Label(self, text="Find and Save Contours")

        # Buttons
        self.save_contour_btn = tkinter.Button(self, text="Save contour", command=self.save_contours)
        self.get_contours_btn = tkinter.Button(self, text="Get contours", command=self.get_contours)

        # Combo Boxes
        self.matchable_contour_cbox = ttk.Combobox(self, textvariable=self.matchable_contour_cbox_var)
        self.matchable_contour_cbox.bind('<<ComboboxSelected>>', self.select_contour)

        # Positioning
        self.panel_label.grid(row=0, column=0)
        self.get_contours_btn.grid(row=1, column=0,sticky='w')
        self.matchable_contour_cbox.grid(row=2, column=0, sticky='w')
        self.save_contour_btn.grid(row=3, column=0, sticky='w')

        # Events
        self.on_get_contours = Event()
        self.on_save_contours_before = Event()
        self.on_save_contours_after = Event()

    def get_contours(self):
        logger.debug("Getting and setting contours for matching")
        ids = ['<all>']
        self.current_contours = {}
        counter = 0
        c_name = f"new {counter}"
        for cnt in self.image_process.image_contours:
            ref = ContourReference(None, None, None, ReferenceType(None, "hsv contour"),
                                   self.image_process, cnt, c_name)
            ref.name = f"new {counter}"
            self.current_contours[ref.name] = ref
            ids.append(ref.name)
            counter += 1

        self.matchable_contour_cbox['values'] = ids
        self.on_get_contours()

    def add_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.add_tracker(self.test_tracker)

    def remove_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.remove_tracker(self.test_tracker)

    def select_contour(self, event):
        c_name = self.matchable_contour_cbox_var.get()
        logger.debug(f"Setting selected contour to {c_name}")
        self.remove_test_tracker()
        if c_name != '<all>':
            cnt_ref: ContourReference = self.current_contours.get(c_name)
            cnt_ref.name = self.image_process.name
            self.test_tracker = Tracker(cnt_ref)
            self.add_test_tracker()
            self.current_contour = cnt_ref

    def save_contours(self):
        im_proc = self.image_process
        if self.current_contour is None:
            self.current_contour = ContourReference(None, image_process=im_proc)
            self.current_contour.name = im_proc.name
            self.current_contour.image_process.set_args()
        self.current_contour.save()
        self.matchable_contour_cbox['values'] = []
        self.remove_test_tracker()


class ColorGetter(SubPanel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = parent
        self.image_processor = ImageProcessor()

        self.x = 0
        self.y = 0
        self.x_cap = 960 - 1
        self.y_cap = 540 - 1

        self.x_slider = tkinter.Scale(self, from_=0, to=self.x_cap, resolution=1,
                                      length=350,
                                      orient=tkinter.HORIZONTAL, command=self.update_coords)

        self.y_slider = tkinter.Scale(self, from_=0, to=self.y_cap, resolution=1,
                                      length=350,
                                      orient=tkinter.HORIZONTAL, command=self.update_coords)

        self.color_table = Table(self, ['variable', 'value'], height=2)
        self.panel_label = tkinter.Label(self, text="HSV Color Getter")

        self.panel_label.grid(row=0, column=0, sticky='w')
        self.x_slider.grid(row=2, column=0, columnspan=3 ,sticky='w')
        self.y_slider.grid(row=3, column=0, columnspan=3, sticky='w')
        self.color_table.grid(row=1, column=0, columnspan=3, sticky='w')

        # Event registration
        self.image_processor.on_process_images += self.draw_cross
        self.image_processor.on_process_images += self.get_color

    def update_coords(self, event):
        self.x = int(self.x_slider.get())
        self.y = int(self.y_slider.get())

    def draw_cross(self):
        output_image = self.image_processor.frames["main output"].get_main_image()
        drawing_utils.draw_line_from_points(output_image,
                                            Point(0, self.y),
                                            Point(self.x_cap, self.y), util_consts.RGBColors.LIGHT_RED)
        drawing_utils.draw_line_from_points(output_image,
                                            Point(self.x, 0),
                                            Point(self.x, self.y_cap), util_consts.RGBColors.LIGHT_RED)

    def get_color(self):
        hsv_image = self.image_processor.frames["main color"].images["hsv"]
        color = hsv_image[self.y, self.x]
        self.color_table.update_value("HSV Float",
                                      (f"%.2f" % (color[0] / 255),
                                       f"%.2f" % (color[1] / 255),
                                       f"%.2f" % (color[2] / 255)))
        self.color_table.update_value("HSV Byte", color)

    def destroy(self):
        self.image_processor.on_process_images -= self.draw_cross
        self.image_processor.on_process_images -= self.get_color
        super().destroy()
