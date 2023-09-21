from PIL import ImageTk, Image
import tkinter

from Client.switch_bot import SwitchBot
from Client.ui.widgets.footer import Footer
from Client.ui.widgets.footers.debug_footer import DebugFooter
from Client.ui.widgets.image_preview import ImagePreview
from Client.ui.widgets.side_panel import SideBar


class FrontEnd:
    def __init__(self, bot: SwitchBot):
        self.bot = bot
        bot.start_main_loop()
        self.WINDOW = tkinter.Tk()
        self.WINDOW.title("SwitchBot")
        self.WINDOW.geometry("1600x900")
        self.WINDOW.grid_propagate(False)
        self.left_pane = tkinter.Frame(self.WINDOW, height=900, width=970)
        self.left_pane.grid_propagate(False)
        self.left_pane.parent = self.WINDOW
        self.preview = ImagePreview(self.left_pane, bot)
        self.sidebar = SideBar(self.WINDOW, bot)
        self.footer = DebugFooter(self.left_pane, bot)
        self.left_pane.grid(row=0, column=0)
        self.sidebar.FRAME.grid(row=0, column=1)
        self.preview.FRAME.grid(row=0, column=0, sticky='n')
        self.footer.FRAME.grid(row=1, column=0, sticky='n')
