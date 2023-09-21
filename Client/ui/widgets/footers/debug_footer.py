import tkinter
from tkinter import ttk

from Client.data.bank import DataBank
from Client.ui.widgets.footer import Footer


class DebugFooter(Footer):
    def __init__(self, parent, bot):
        super().__init__(parent, bot)
        # Widget variables
        self.debug_list = []
        self.data_bank = DataBank()

        # Widget Creation
        self.debug_table_cols = ['variable', 'value']
        self.debug_table_header = tkinter.Label(self.FRAME, text="Debuging Variables")
        self.debug_table = ttk.Treeview(self.FRAME, columns=self.debug_table_cols,show="headings")
        self.debug_table.heading("variable", text="Variable")
        self.debug_table.heading("value", text="Value")

        # Widget Config

        # Positioning
        self.debug_table_header.grid(row=0, column=0, sticky='ew')
        self.debug_table.grid(row=1, column=0, sticky='nws')

        # Event Registration
        self.data_bank.debug_entry_events.register_new_event("on_debug_change", self.update_debug_values)

    def update_debug_values(self, event_args):
        arg_name = event_args.arg_name
        arg_value = event_args.arg_value
        if arg_name in self.debug_list:
            index = self.debug_list.index(arg_name)
            item = self.debug_table.get_children()[index]
            self.debug_table.item(item, text='', values=(arg_name, arg_value))
        else:
            self.debug_list.append(arg_name)
            self.debug_table.insert('', -1, values=(arg_name, arg_value))


