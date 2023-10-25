import tkinter
from tkinter import ttk

from Client.common_utils.models import Event, ReactiveList


class Table(ttk.Treeview):
    def __init__(self, parent, column_names, *args, **kwargs):
        super().__init__(parent, columns=column_names, show='headings',*args, **kwargs)
        self.root = parent
        self.column_names = column_names
        self.entry_list = []
        for name in column_names:
            self.heading(name, text=name.lower().capitalize())

    def update_value(self, arg_name=None, arg_value=None):
        if arg_name in self.entry_list:
            index = self.entry_list.index(arg_name)
            item = self.get_children()[index]
            self.item(item, text='', values=(arg_name, arg_value))
        else:
            self.entry_list.append(arg_name)
            self.insert('', -1, values=(arg_name, arg_value))


class ObjectTable(ttk.Treeview):
    def __init__(self, parent, mapping: dict[str: str], p_list: ReactiveList, *args, **kwargs):

        super().__init__(parent, columns=list(mapping.values()), selectmode="browse", show='headings', *args, **kwargs)
        self.objects = p_list
        self.headings = mapping.values()
        for k, v in mapping.items():
            self.heading(str(v), text=str(k))
            width = 100
            if v == "_id":
                width = 50
            self.column(v, minwidth=20, width=width)

        # Events
        self.on_list_change = Event()
        self.on_object_selected = Event()
        self.bind("<<TreeviewSelect>>", self.on_selection)

        # Event Registration
        self.objects.on_added_item += self.add_row
        self.objects.on_removed_item += self.remove_row
        self.objects.on_entry_changed += self.update_row
        self.objects.on_list_cleared += self.reset_table_data

        # Finalize Init
        self.reset_table_data()

    def reset_table_data(self):
        self.delete(*self.get_children())
        for obj in self.objects:
            self.insert('', -1, values=self.get_values(obj))

    def on_selection(self, event):
        obj = self.objects[self.index(self.focus())]
        self.on_object_selected(obj)

    def remove_row(self, index):
        item = self.get_children()[index]
        self.delete(item)

    def add_row(self, obj):
        values = []
        self.insert('', tkinter.END, values=tuple(self.get_values(obj)))

    def update_row(self, obj):
        if obj in self.objects:
            index = self.objects.index(obj)
            item = self.get_children()[index]
            self.item(item, text='', values=tuple(self.get_values(obj)))

    def get_values(self, obj):
        values = []
        for head in self.headings:
            s_obj = obj
            for sub_str in head.split('.'):
                if sub_str == "_id":
                    s_obj = s_obj.get_id()
                else:
                    s_obj = getattr(s_obj, sub_str)
            values.append(s_obj)
        return tuple(values)
