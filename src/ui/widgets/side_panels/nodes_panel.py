import tkinter

from src.navigation.nodes import NodeMapping
from src.ui.widgets.side_panels.side_panel import SidePanel
from src.ui.widgets.sub_panels.node_panels import CreateNodePanel


class NodesPanel(SidePanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_nodes_panel = CreateNodePanel(self)

        self.create_nodes_panel.grid(row=0, column=0)