import tkinter, logging
from tkinter import ttk

import cv2
from PIL import ImageTk, Image

from Client.imaging.processing import ImageProcessor
from Client.models.core import Point

logger = logging.getLogger(__name__)


class ImagePreview:
    def __init__(self, parent, bot):
        self.bot = bot
        self.parent = parent
        self.FRAME = tkinter.Frame(parent, highlightbackground="gray", highlightthickness=3, height=575, width=970)
        self.FRAME.grid_propagate(False)

        # Singletons
        self.image_processor = ImageProcessor()

        self.main_image = tkinter.Label(self.FRAME, width=960, height=540)
        self.secondary_image_size = (96*3, 54*3)
        self.secondary_image_point = Point(25,25)

        # Image Selection - Main
        self.image_selection_frame = tkinter.Frame(self.FRAME, height=30, width=960)
        self.main_selection = tkinter.StringVar()
        self.image_options = ['None']
        self.main_selection_label = tkinter.Label(self.image_selection_frame, text="Main Image: ")
        self.main_selection_cbox = ttk.Combobox(
            self.image_selection_frame,
            textvariable=self.main_selection
        )
        self.main_selection_cbox['values'] = self.image_options
        self.main_selection_cbox.bind('<<ComboboxSelected>>', self.on_main_output_change)
        for im_proc_name, im_proc in self.image_processor.frames.items():
            self.image_options.append(im_proc_name)
        self.update_options(self.main_selection_cbox, self.image_options)

        # Image Selection - Secondary
        self.secondary_selection = tkinter.StringVar()
        self.secondary_selection_label = tkinter.Label(self.image_selection_frame, text="Secondary Image: ")
        self.secondary_selection_cbox = ttk.Combobox(
            self.image_selection_frame,
            textvariable=self.secondary_selection
        )
        self.main_selection.set("main output")
        self.secondary_selection_cbox.bind('<<ComboboxSelected>>', self.on_secondary_output_change)
        self.update_options(self.secondary_selection_cbox, self.image_options)

        # Positioning
        self.main_image.grid(row=0, column=0, sticky="nsew")
        self.image_selection_frame.grid(row=1, column=0, sticky='sw')
        self.main_selection_label.grid(row=0,column=0, sticky='w')
        self.main_selection_cbox.grid(row=0, column=1, sticky='w')
        self.secondary_selection_label.grid(row=0,column=2, sticky='w')
        self.secondary_selection_cbox.grid(row=0, column=3, sticky='w')

        # Finalize init
        self.update_options(self.secondary_selection_cbox, self.image_options)
        self.update_options(self.main_selection_cbox, self.image_options)
        self.FRAME.after(1000, self.update_image)

    def on_main_output_change(self, event):
        self.image_processor.set_output_image(self.main_selection.get())

    def on_secondary_output_change(self, event):
        self.image_processor.set_output_image(self.secondary_selection.get(), secondary=True)

    def update_options(self, cbox, options):
        self.image_options = options
        cbox['values'] = options

    def update_image(self):
        im = self.image_processor.get_combined_output_frame()
        if im is not None:
            im = ImageTk.PhotoImage(image=Image.fromarray(im).resize((960, 540)))
            self.main_image.configure(image=im)
            self.main_image.image = im
        self.FRAME.after(32, self.update_image)
