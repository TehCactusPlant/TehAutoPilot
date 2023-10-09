import tkinter

from Client.navigation.nodes import NodeMapping
from Client.ui.widgets.side_panels.side_panel import SidePanel


class NodesPanel(SidePanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.rowconfigure(9, {'minsize': 10})
        self.columnconfigure(9, {'minsize': 5})

        self.header = tkinter.Label(self, text='Nodes')
        # Create Node
        self.create_node_manual_btn = tkinter.Button(self, text="Manual Node", width=10)
        self.create_node_auto_btn = tkinter.Button(self, text="Auto Node", width=10)
        self.delete_node_btn = tkinter.Button(self, text="Delete Node", width=10)
        self.link_node_btn = tkinter.Button(self, text="Link Node", width=10)
        self.link_node_text_box = tkinter.Entry(self)
        self.delete_node_text_box = tkinter.Entry(self)

        # Delete Node
        # Link Node
        # Node Map

        #Grids
        self.header.grid(row=0, column=2, sticky='ne')
        self.create_node_manual_btn.grid(row=1, column=0)
        self.create_node_auto_btn.grid(row=2, column=0)
        self.delete_node_btn.grid(row=3, column=0)
        self.delete_node_text_box.grid(row=3, column=1)
        self.link_node_btn.grid(row=4, column=0)
        self.link_node_text_box.grid(row=4, column=1)

        self.create_node_manual_btn.configure(command=self.create_node_manual)
        self.delete_node_btn.configure(command=self.delete_node)

    def create_node_manual(self):
        # nav: NodeNavigator = self.bot.node_navigator
        # c_img = self.bot.image_processor.bot_frame
        # nav.create_new_node(c_img)
        self.bot.image_processor.test_tracker()

    def create_node_auto(self):
        pass

    def delete_node(self):
        for tracker in self.bot.data_bank.trackers:
            self.bot.data_bank.remove_tracker(tracker)
    def link_node(self):
        pass