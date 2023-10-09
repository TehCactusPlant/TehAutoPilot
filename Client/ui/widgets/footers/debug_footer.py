import tkinter, logging
from tkinter import ttk
from Client.data.bank import DataBank
from Client.imaging.processing import ImageProcessor
from Client.input_handling.management import InputManager
from Client.ui.widgets.custom_elements import Table
from Client.ui.widgets.footers.footer import Footer

logger = logging.getLogger(__name__)


class DebugFooter(Footer):
    def __init__(self, parent):
        super().__init__(parent)
        self.input_manager = InputManager()

        # Widget variables
        self.debug_list = []
        self.data_bank = DataBank()
        self.manual_control_flag = tkinter.IntVar(value=1)
        self.show_special_output_flag = tkinter.IntVar(value=0)

        # Widget Creation
        self.debug_table_header = tkinter.Label(self, text="Debugging Variables")
        self.debug_table = Table(self, ['variable', 'value'])
        self.manual_control_toggle = tkinter.Checkbutton(
            self, text="Manual Control",
            variable=self.manual_control_flag, onvalue=1, offvalue=0, command=self.toggle_manual_control)
        self.special_output_toggle = tkinter.Checkbutton(
            self, text="External Display",
            variable=self.show_special_output_flag, onvalue=1, offvalue=0, command=self.toggle_special_display)

        # Widget Config

        # Positioning
        self.debug_table_header.grid(row=0, column=0, sticky='ew')
        self.debug_table.grid(row=1, column=0, sticky='nws')
        self.manual_control_toggle.grid(row=0, column=1)
        self.special_output_toggle.grid(row=0, column=2)
        # Event Registration
        self.data_bank.on_debug_entry_change += self.debug_table.update_value

    def toggle_manual_control(self):
        value = self.manual_control_flag.get()
        value = True if value == 1 else False
        logger.debug(f"Toggling Manual Control state to {value}")
        InputManager().controller.set_automation_state(value)

    def toggle_special_display(self):
        value = self.show_special_output_flag.get()
        value = True if value == 1 else False
        logger.debug(f"Toggling state to {value}")
        ImageProcessor().toggle_run_special(value)
