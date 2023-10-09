import tkinter, logging
from tkinter import ttk

from Client.imaging.processing import ImageProcessor
from Client.models.core import ImageProcess
from Client.models.image_process import HSVImageProcess
from Client.ui.widgets.custom_elements import Table
from Client.ui.widgets.side_panels.side_panel import SidePanel
from Client.ui.widgets.sub_panels.combo_panels import HSVContourPanel
from Client.ui.widgets.sub_panels.image_panels import ImageProcessHSVAdjuster, ContourMatchingPanel, ColorGetter

logger = logging.getLogger(__name__)


class HSVTestPanel(SidePanel):
    def __init__(self, parent):
        # Base Init
        super().__init__(parent)
        self.image_processor = ImageProcessor()
        self.editor_panel = HSVContourPanel(self, self.image_processor.frames["main hsv"], None)
        self.im_proc_table = Table(self, ["variable", "value"])

        # Variables
        self.color_range_presets = ImageProcess.get_all()
        self.color_range_preset_names = []

        # Tkinter Variables
        self.hsv_process_cbox_var = tkinter.StringVar()

        # Combo Box
        self.load_process_label = tkinter.Label(self, text="Load ImageProcess: ")
        self.load_color_range_preset_cbox = ttk.Combobox(
            self, textvariable=self.hsv_process_cbox_var)
        self.load_color_range_preset_cbox.bind('<<ComboboxSelected>>', self.change_hsv_preset)

        # Others
        self.hsv_getter = ColorGetter(self)

        # Positioning
        self.load_process_label.grid(row=0, column=0, sticky='w')
        self.load_color_range_preset_cbox.grid(row=0, column=1, sticky='w')
        self.editor_panel.grid(row=2, column=0, sticky='w', columnspan=2)
        self.im_proc_table.grid(row=1, column=0, columnspan=3, sticky='w')
        self.hsv_getter.grid(row=3, column=0, sticky='w', columnspan=3)
        # Event Registration
        self.editor_panel.main_hsv_adjuster.on_save_hsv_image_process += self.reload_color_preset_names

        # Finalize Init
        self.reload_color_preset_names()
        self.hsv_process_cbox_var.set("<new>")
        self.editor_panel.main_hsv_adjuster.preset_name_var = self.hsv_process_cbox_var

    def reload_color_preset_names(self):
        self.color_range_preset_names = ["<new>"]
        for key in self.color_range_presets.keys():
            self.color_range_preset_names.append(key)
        self.load_color_range_preset_cbox['values'] = self.color_range_preset_names

    def change_hsv_preset(self, event):
        current_sel = self.hsv_process_cbox_var.get()
        logger.info(f"Changing to HSV preset: {current_sel}")
        is_main = False
        if current_sel == "<new>":
            im_proc = self.image_processor.frames["main hsv"]
        else:
            im_proc = self.color_range_presets[current_sel]
            im_proc = HSVImageProcess(im_proc.get_id())
            im_proc.update_show_contours(True)
            self.editor_panel.main_hsv_adjuster.show_contours_flag.set(1)
            self.color_range_presets[current_sel] = im_proc
            self.editor_panel.main_hsv_adjuster.image_process = im_proc
            _min, _max = (
                int(im_proc.args.get_arg_value("h_min")),
                int(im_proc.args.get_arg_value("s_min")),
                int(im_proc.args.get_arg_value("v_min")),), \
                (
                int(im_proc.args.get_arg_value("h_max")),
                int(im_proc.args.get_arg_value("s_max")),
                int(im_proc.args.get_arg_value("v_max"))
            )
            self.editor_panel.main_hsv_adjuster.set_slider_values_hex(_min, _max)
            self.update_image_process(im_proc)

    def update_image_process(self, im_proc: HSVImageProcess):
        if self.editor_panel.main_hsv_adjuster.image_process != self.image_processor.frames["main hsv"]:
            self.image_processor.remove_image_process(self.editor_panel.main_hsv_adjuster.image_process)
        self.image_processor.add_image_process(im_proc)
        self.editor_panel.main_hsv_adjuster.image_process = im_proc
        self.editor_panel.main_save_contours_panel.image_process = im_proc
        self.im_proc_table.update_value("ID", im_proc.get_id())
        self.im_proc_table.update_value("Name", im_proc.name)
        self.im_proc_table.update_value("hsv_min", im_proc.min_hsv)
        self.im_proc_table.update_value("hsv_max", im_proc.max_hsv)

    def destroy(self):
        self.editor_panel.main_hsv_adjuster.on_save_hsv_image_process -= self.reload_color_preset_names
        super().destroy()
