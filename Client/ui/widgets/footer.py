import tkinter

from Client.switch_bot import SwitchBot


class Footer:
    def __init__(self, parent, bot: SwitchBot):
        self.FRAME = tkinter.Frame(parent, width=970, height=325, highlightbackground="gray", highlightthickness=3)
        self.FRAME.grid_propagate(False)
        self.bot = bot
