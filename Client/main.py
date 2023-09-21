from Client.switch_bot import SwitchBot
from Client.ui.bot_front_end import FrontEnd

if __name__ == "__main__":
    bot = SwitchBot("pkmnbdsp")
    bot.start_main_loop()
    # Tkinter
    fe = FrontEnd(bot)
    fe.WINDOW.mainloop()
