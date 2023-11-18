from src.switch_bot import SwitchBot
from src.ui.bot_front_end import FrontEnd
import logging, coloredlogs

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger, level=logging.DEBUG)

if __name__ == "__main__":
    # Main
    bot = SwitchBot("pkmnbdsp")
    bot.start_main_loop()

    # Tkinter
    fe = FrontEnd(bot)
    fe.WINDOW.mainloop()
