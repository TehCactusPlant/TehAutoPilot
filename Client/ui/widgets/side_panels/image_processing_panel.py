import tkinter, colorsys, logging, numpy
from tkinter import ttk
from PIL import Image, ImageTk

from Client.imaging.processing import ImageProcessor
from Client.imaging.scanning import ImageScanner, Tracker
from Client.models.core import ImageProcess, Arg, ContourPoints, ReferenceType, Reference, ArgEntry
from Client.models.image_process import HSVImageProcess
from Client.models.matching import ContourReference
from Client.ui.widgets.side_panels.side_panel import SidePanel

logger = logging.getLogger(__name__)


class HSVTestPanel(SidePanel):
    def __init__(self, parent, bot):
        super().__init__(parent, bot)

        self._blank_img = numpy.ones(shape=[25, 25, 3], dtype=numpy.uint8)
        self.min_hsv_img = self._blank_img
        self.max_hsv_img = self._blank_img
        self.image_processor = ImageProcessor()
        self.image_scanner = ImageScanner()

        self.general_contour_process: HSVImageProcess = self.image_processor.get_image_process("main hsv")
        self.current_contours = {}
        self.test_tracker: Tracker = None

        # TK Variables
        self.show_contours_flag = tkinter.IntVar()

        # UI Elements
        self.show_contours_toggle = tkinter.Checkbutton(
            self.FRAME, text="Show Contours",
            variable=self.show_contours_flag, onvalue=1, offvalue=0, command=self.update_show_contours)
        self.h_label = tkinter.Label(self.FRAME, text="H")
        self.s_label = tkinter.Label(self.FRAME, text="S")
        self.v_label = tkinter.Label(self.FRAME, text="V")
        self.hsv_min_label = tkinter.Label(self.FRAME, text="Min")
        self.hsv_max_label = tkinter.Label(self.FRAME, text="Max")

        self.min_h_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_h_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.min_s_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_s_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.min_v_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)
        self.max_v_slider = tkinter.Scale(self.FRAME, from_=0, to=1, resolution=0.01,
                                          orient=tkinter.HORIZONTAL, command=self.update_hsv)

        self.get_contours_btn = tkinter.Button(self.FRAME, text="Get contours", command=self.get_contours)
        self.load_contour_cbox_name_var = tkinter.StringVar()
        self.matchable_contour_cbox_var = tkinter.StringVar()
        self.matchable_contour_cbox = ttk.Combobox(self.FRAME, textvariable=self.matchable_contour_cbox_var)
        self.matchable_contour_cbox.bind('<<ComboboxSelected>>', self.on_contour_selection_change)

        self.save_contour_btn = tkinter.Button(self.FRAME, text="Save contour", command=self.save_contours)
        self.matchable_contour_cbox = ttk.Combobox(self.FRAME, textvariable=self.matchable_contour_cbox_var)
        self.matchable_contour_cbox.bind('<<ComboboxSelected>>', self.set_selected_contour)

        self.min_img = tkinter.Label(self.FRAME, width=25, height=25)
        self.max_img = tkinter.Label(self.FRAME, width=25, height=25)

        self.color_range_preset_entry_var = tkinter.StringVar()
        self.color_range_preset_entry_cbox_var = tkinter.StringVar()
        self.color_range_presets: dict[str:ImageProcess] = ImageProcess.get_all()
        self.color_range_preset_names = []

        self.create_color_range_preset_btn = tkinter.Button(self.FRAME, text="Save new Preset",
                                                            command=self.save_color_range_preset)
        self.load_color_range_preset_label = tkinter.Label(self.FRAME, text="Load Preset: ")

        # Image process
        self.load_color_range_preset_cbox = ttk.Combobox(
            self.FRAME, textvariable=self.color_range_preset_entry_cbox_var)
        self.load_color_range_preset_cbox.bind('<<ComboboxSelected>>', self.on_color_range_preset_change)

        # Positioning
        self.load_color_range_preset_label.grid(row=0, column=0)
        self.load_color_range_preset_cbox.grid(row=0, column=1)
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
        self.create_color_range_preset_btn.grid(row=5, column=0, columnspan=3, sticky='ew')
        self.min_img.grid(row=6, column=1)
        self.max_img.grid(row=6, column=2)

        # self.save_contour_btn
        self.get_contours_btn.grid(row=1, column=3,sticky='w')
        self.matchable_contour_cbox.grid(row=2, column=3, sticky='w')
        self.save_contour_btn.grid(row=4, column=3, sticky='w')

        # Finalize init
        self.reload_color_preset_names()
        self.update_hsv(None)

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
        self.general_contour_process.set_hsv_range(int_hsv_min, int_hsv_max)

    def reload_color_preset_names(self):
        self.color_range_preset_names = []
        for key, value in self.color_range_presets.items():
            self.color_range_preset_names.append(key)
        self.load_color_range_preset_cbox['values'] = self.color_range_preset_names

    def on_color_range_preset_change(self, event):
        current_sel = self.color_range_preset_entry_cbox_var.get()
        logger.info(f"Changing to HSV preset: {current_sel}")
        im_proc = self.color_range_presets[current_sel]
        self.min_h_slider.set(str(int(im_proc.args.get_arg_value("h_min")) / 255))
        self.min_s_slider.set(str(int(im_proc.args.get_arg_value("s_min")) / 255))
        self.min_v_slider.set(str(int(im_proc.args.get_arg_value("v_min")) / 255))
        self.max_h_slider.set(str(int(im_proc.args.get_arg_value("h_max")) / 255))
        self.max_s_slider.set(str(int(im_proc.args.get_arg_value("s_max")) / 255))
        self.max_v_slider.set(str(int(im_proc.args.get_arg_value("v_max")) / 255))

    def save_color_range_preset(self):
        preset_name = self.color_range_preset_entry_cbox_var.get()
        if preset_name is None or preset_name == "":
            logger.warning(f"Preset name is blank. Preset cannot be saved.")
            return
        _min = numpy.array([self.min_h_slider.get(),
                            self.min_s_slider.get(),
                            self.min_v_slider.get()])
        _max = numpy.array([self.max_h_slider.get(),
                            self.max_s_slider.get(),
                            self.max_v_slider.get()])

        int_hsv_min = _min * 255
        int_hsv_max = _max * 255
        if preset_name in self.color_range_preset_names:
            im_proc: ImageProcess = self.color_range_presets[preset_name]
            im_proc.args.update_arg("h_min", int(int_hsv_min[0]))
            im_proc.args.update_arg("s_min", int(int_hsv_min[1]))
            im_proc.args.update_arg("v_min", int(int_hsv_min[2]))
            im_proc.args.update_arg("h_max", int(int_hsv_max[0]))
            im_proc.args.update_arg("s_max", int(int_hsv_max[1]))
            im_proc.args.update_arg("v_max", int(int_hsv_max[2]))

        else:
            im_proc: ImageProcess = ImageProcess(None, preset_name, None)
            im_proc.args.add_arg(Arg(None, "h_min", int(int_hsv_min[0])))
            im_proc.args.add_arg(Arg(None, "s_min", int(int_hsv_min[1])))
            im_proc.args.add_arg(Arg(None, "v_min", int(int_hsv_min[2])))
            im_proc.args.add_arg(Arg(None, "h_max", int(int_hsv_max[0])))
            im_proc.args.add_arg(Arg(None, "s_max", int(int_hsv_max[1])))
            im_proc.args.add_arg(Arg(None, "v_max", int(int_hsv_max[2])))

        im_proc.save()
        self.color_range_presets[preset_name] = im_proc
        self.reload_color_preset_names()

    def get_contours(self):
        logger.debug("Getting and setting contours for matching")
        ids = ['none']
        self.current_contours = {}
        counter = 0
        for cnt in self.general_contour_process.image_contours:
            ref = ContourReference(None, None, None, ReferenceType(None, "hsv contour"),
                                   self.general_contour_process, cnt)
            print(ref.reference_type.get_id())

            ref.name = f"new {counter}"
            self.current_contours[ref.name] = ref
            ids.append(ref.name)
            counter += 1

        self.matchable_contour_cbox['values'] = ids

    def update_show_contours(self, value=None):
        if value is None:
            value = self.show_contours_flag.get()
        else:
            self.show_contours_flag.set(value)
        show_conts = True if value == 1 else False
        self.image_processor.frames["main hsv"].update_show_contours(show_conts)

    def add_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.add_tracker(self.test_tracker)
            self.update_show_contours(0)

    def remove_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.remove_tracker(self.test_tracker)
            self.update_show_contours(1)

    def set_selected_contour(self, event):
        c_name = self.matchable_contour_cbox_var.get()
        logger.debug(f"Setting selected contour to {c_name}")
        self.remove_test_tracker()
        if c_name != 'none':
            t_name = self.color_range_preset_entry_cbox_var.get()
            cnt_ref: ContourReference = self.current_contours.get(c_name)
            self.test_tracker = Tracker(cnt_ref, t_name)
            self.add_test_tracker()

    def save_contours(self):
        cnt_ref: ContourReference = self.test_tracker.image_reference
        name = self.load_contour_cbox_name_var.get()
        if cnt_ref.args is None:
            cnt_ref.args = ArgEntry(None, name)
            cnt_ref.args.add_arg(Arg(None, "contours", cnt_ref.contour_points.contours))
        else:
            cnt_ref.args.update_arg("contours", cnt_ref.contour_points.contours)
        cnt_ref.save()

    def on_contour_selection_change(self, event):
        pass
