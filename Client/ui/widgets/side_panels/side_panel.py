import tkinter


class SidePanel(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=624, height=874, highlightbackground="blue", highlightthickness=3)
        self.root = parent
        self.grid_propagate(False)
