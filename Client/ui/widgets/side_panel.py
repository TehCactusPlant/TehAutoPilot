import tkinter, logging
from tkinter import ttk
from Client.ui.widgets.side_panels.image_processing_panel import HSVTestPanel
from Client.ui.widgets.side_panels.nodes_panel import NodesPanel
logger = logging.getLogger(__name__)

class SideBar:
    default_options = ("Default", "Nodes", "HSV")

    def __init__(self,parent, bot):
        self.bot = bot
        self.parent = parent
        self.FRAME = tkinter.Frame(parent, width=630, height=900, highlightbackground="gray", highlightthickness=3)
        self.FRAME.grid_propagate(False)
        self.selection = tkinter.StringVar()
        self.options_label = tkinter.Label(self.FRAME, text='Current Panel:')
        self.current_panel = None
        self.options_box = ttk.Combobox(
            self.FRAME,
            textvariable=self.selection
        )
        self.options_box['values'] = self.default_options
        self.options_box.bind('<<ComboboxSelected>>', self.change_option)
        self.options_box.grid(row=0, column=1, sticky='nw')
        self.options_label.grid(row=0, column=0, sticky='ne')

    def change_option(self, event):
        sel = self.selection.get()
        logger.info(f"Panel changed to {sel}")
        if self.current_panel is not None:
            self.current_panel.FRAME.destroy()
        if sel == "Nodes":
            self.current_panel = NodesPanel(self.FRAME, self.bot)
            self.current_panel.FRAME.grid(row=1, column=0, columnspan=2)
        elif sel == "HSV":
            self.current_panel = HSVTestPanel(self.FRAME, self.bot)
            self.current_panel.FRAME.grid(row=1, column=0, columnspan=2)
