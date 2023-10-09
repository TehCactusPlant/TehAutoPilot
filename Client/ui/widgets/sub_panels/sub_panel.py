import tkinter


class SubPanel(tkinter.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, highlightbackground="gray", highlightthickness=1, *args, **kwargs)
        self.root = parent
