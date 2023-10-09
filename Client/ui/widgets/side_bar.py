import tkinter, logging
from tkinter import ttk
from Client.ui.widgets.side_panels.image_processing_panel import HSVTestPanel
from Client.ui.widgets.side_panels.nodes_panel import NodesPanel
from Client.ui.widgets.side_panels.tracking_panel import TrackingPanel

logger = logging.getLogger(__name__)


class SideBar(tkinter.Frame):
    default_options = ("Nodes", "HSV Imaging", "Tracking")

    def __init__(self, parent):
        super().__init__(parent, width=630, height=900, highlightbackground="gray", highlightthickness=3)
        self.parent = parent
        self.grid_propagate(False)
        self.selection = tkinter.StringVar()
        self.options_label = tkinter.Label(self, text='Current Panel:')
        self.current_panel = None
        self.options_box = ttk.Combobox(
            self,
            textvariable=self.selection
        )
        self.options_box['values'] = self.default_options
        self.options_box.bind('<<ComboboxSelected>>', self.change_option)
        self.options_box.grid(row=0, column=1, sticky='nw')
        self.options_label.grid(row=0, column=0, sticky='ne')

        self.nodes_panel = NodesPanel(self)
        self.imaging_panel = HSVTestPanel(self)
        self.tracking_panel = TrackingPanel(self)

    def change_option(self, event):
        sel = self.selection.get()
        logger.info(f"Panel changed to {sel}")
        if self.current_panel is not None:
            self.current_panel.grid_remove()
        if sel == "Nodes":
            self.current_panel = self.nodes_panel
            self.current_panel.grid(row=1, column=0, columnspan=2)
        elif sel == "HSV Imaging":
            self.current_panel = self.imaging_panel
            self.current_panel.grid(row=1, column=0, columnspan=2)
        elif sel == "Tracking":
            self.current_panel = self.tracking_panel
            self.current_panel.grid(row=1, column=0, columnspan=2)
