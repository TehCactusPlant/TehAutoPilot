import tkinter

from Client.switch_bot import SwitchBot


class Footer(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=970, height=325, highlightbackground="gray", highlightthickness=3)
        self.root = parent
        self.grid_propagate(False)
