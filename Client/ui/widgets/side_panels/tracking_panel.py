import logging
import tkinter
from tkinter import ttk

from Client.data.bank import DataBank
from Client.imaging.processing import ImageProcessor
from Client.imaging.scanning import ImageScanner, Tracker
from Client.models.core import Reference
from Client.common_utils.models import Event
from Client.ui.widgets.custom_elements import ObjectTable

from Client.ui.widgets.side_panels.side_panel import SidePanel
from Client.ui.widgets.sub_panels.combo_panels import HSVContourPanel

logger = logging.getLogger(__name__)


class TrackingPanel(SidePanel):
    def __init__(self, parent):
        # Base Init
        super().__init__(parent)
        self.image_processor = ImageProcessor()
        self.image_scanner = ImageScanner()
        self.current_tracker = None

        # TK Variables
        self.tracker_selection = tkinter.StringVar()
        self.active_tracker_names = tkinter.StringVar(value=[])
        self.data_bank = DataBank()
        self.references = self.data_bank.references
        self.reference_names = []

        # Details table
        self.tracker_detail_table = ObjectTable(self,
                                                {
                                                    "Name": "name",
                                                    "Img. Proc. ID": "image_reference.image_process._id",
                                                    "Img. Proc. Name": "image_reference.image_process.name",
                                                    "Reference ID": "image_reference._id",
                                                    "Reference Name": "image_reference.name"
                                                }, self.image_scanner.trackers)

        self.editor_panel = None

        # Combobox
        self.reference_selection_cbox = ttk.Combobox(self, textvariable=self.tracker_selection)
        self.load_tracker_btn = tkinter.Button(self, text="Load Tracker", command=self.load_tracker)
        # Events
        self.on_tracker_load = Event()

        # Event Registration
        self.tracker_detail_table.on_object_selected += self.select_tracker
        # Positioning
        self.reference_selection_cbox.grid(row=0, column=0, sticky='w')
        self.load_tracker_btn.grid(row=0,column=1, sticky='w')
        self.tracker_detail_table.grid(row=1, column=0, columnspan=4)

        # Finalize Init
        self.update_tracker_selections()
        pass

    def load_tracker(self):
        selection = self.tracker_selection.get()
        logger.debug(f"Changing selected tracker to {selection}")
        ref = self.references.get_variable_value(selection)
        if ref is not None:
            tracker = Tracker(ref)
            logger.debug(f"Loading/Creating new Tracker, ref_type {tracker.image_reference.reference_type.name}")
            self.add_tracker(tracker)

        self.on_tracker_load()

    def select_tracker(self, tracker):
        logger.debug(f"Switching selected tracker to {tracker.name}")
        if tracker is not None:
            logger.debug(f"Selected tracker found:\nName: {tracker.name}. Initializing tracker editor")

            self.current_tracker = tracker
            if self.editor_panel is not None:
                self.editor_panel.destroy()
                logger.debug("Old Tracker Panel Editor destroyed.")
                self.editor_panel = None
        else:
            logger.warning(f"Somehow None was passed to select_tracker...")
            return

        im_proc = tracker.image_reference.image_process
        _min, _max = (
            int(im_proc.args.get_arg_value("h_min")),
            int(im_proc.args.get_arg_value("s_min")),
            int(im_proc.args.get_arg_value("v_min")),), \
            (
                int(im_proc.args.get_arg_value("h_max")),
                int(im_proc.args.get_arg_value("s_max")),
                int(im_proc.args.get_arg_value("v_max"))
            )
        if tracker.image_reference.reference_type.name == "hsv contour":
            logger.debug("tracker.image_reference.reference_type.name tracker found. Creating panel")
            self.editor_panel = HSVContourPanel(self, im_proc, tracker.image_reference)
            self.editor_panel.grid(row=2, column=0, columnspan=3)
            self.editor_panel.main_hsv_adjuster.set_slider_values_hex(_min, _max)
            self.editor_panel.main_save_contours_panel.get_contours_btn["state"] = "disabled"
            self.editor_panel.main_save_contours_panel.matchable_contour_cbox["state"] = "disabled"
            logger.debug("Panel Created and Gridded")

    def add_tracker(self, tracker):
        for i_tracker in self.image_scanner.trackers:
            if tracker.name == i_tracker.name:
                logger.warning("Tracker already loaded. No action taken.")
                return
        self.image_scanner.add_tracker(tracker)

    def remove_tracker(self, tracker):
        self.image_scanner.remove_tracker(tracker)

    def update_tracker_selections(self):
        self.reference_names = [key for key in self.references.get_all()]
        self.reference_selection_cbox["values"] = self.reference_names
