import tkinter

from Client.switch_bot import SwitchBot
from Client.ui.widgets.footers.debug_footer import DebugFooter
from Client.ui.widgets.image_preview import ImagePreview
from Client.ui.widgets.side_bar import SideBar


class FrontEnd:
    def __init__(self, bot: SwitchBot):
        self.WINDOW = tkinter.Tk()
        self.WINDOW.title("SwitchBot")
        self.WINDOW.geometry("1600x900")
        self.WINDOW.grid_propagate(False)
        self.left_pane = tkinter.Frame(self.WINDOW, height=900, width=970)
        self.left_pane.grid_propagate(False)
        self.left_pane.root = self.WINDOW
        self.preview = ImagePreview(self.left_pane)
        self.sidebar = SideBar(self.WINDOW)
        self.footer = DebugFooter(self.left_pane)

        # Positioning
        self.preview.grid(row=0, column=0, sticky='n')
        self.footer.grid(row=1, column=0, sticky='n')
        self.left_pane.grid(row=0, column=0, sticky='w')
        self.sidebar.grid(row=0, column=1, sticky='e')
