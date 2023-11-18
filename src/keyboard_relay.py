import tkinter

from src.input_handling.control import SwitchProPiControllerRelay

RELAY = SwitchProPiControllerRelay()

window = tkinter.Tk()
window.title("KBM Switch")
window.geometry("100x50")
options_frame = tkinter.Frame(window)


def toggle_relay_controls():
    value = relay_controls_flag.get()
    value = True if value == 1 else False
    RELAY.set_automation_state(value)


relay_controls_flag = tkinter.IntVar(value=1)
relay_controls_toggle = tkinter.Checkbutton(options_frame, text="enable_relay", variable=relay_controls_flag,
                                            command=toggle_relay_controls)

relay_controls_toggle.grid(row=0, column=0)
options_frame.grid(row=0, column=0)

if __name__ == "__main__":
    RELAY.start_bg_thread()
    window.mainloop()
