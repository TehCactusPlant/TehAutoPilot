import tkinter, logging
from tkinter import ttk

from src.common_utils.models import Event
from src.data.bank import DataBank
from src.imaging.scanning import ImageScanner, Tracker
from src.models.core import Node
from src.navigation.nodes import NodeMapping
from src.ui.widgets.custom_elements import ObjectTable
from src.ui.widgets.sub_panels.sub_panel import SubPanel

logger = logging.getLogger(__name__)


class CreateNodePanel(SubPanel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Init variables
        self.test_tracker = None
        self.image_scanner = ImageScanner()
        self.node_mapper = NodeMapping()
        self.data_bank = DataBank()
        self.location = None
        self.reference = None

        # TK Variables
        self.image_reference_cbox_var = tkinter.StringVar()
        self.location_cbox_var = tkinter.StringVar()

        # Elements
        self.panel_label = tkinter.Label(self, text="Create Node")
        self.reference_label = tkinter.Label(self, text="Reference: ")
        self.location_label = tkinter.Label(self, text="Location: ")

        self.image_reference_cbox = ttk.Combobox(self, textvariable=self.image_reference_cbox_var)
        self.image_reference_cbox.bind('<<ComboboxSelected>>', self.select_reference)

        self.location_cbox = ttk.Combobox(self, textvariable=self.location_cbox_var)
        self.location_cbox.bind('<<ComboboxSelected>>', self.select_location)

        self.loaded_nodes_detail_table = ObjectTable(self,
                                                {
                                                    "ID": "_id",
                                                    "Reference ID": "reference._id",
                                                    "Reference Name": "reference.name",
                                                    "Match": "reference.match"
                                                }, self.node_mapper.mapped_nodes)
        # self.loaded_nodes_detail_table.on_object_selected += self.select_tracker

        self.save_node_button = tkinter.Button(self, text='Save Node', command=self.save_node)

        # Positioning
        self.panel_label.grid(row=0, column=0, sticky='w')
        self.location_label.grid(row=1, column=0, sticky='w')
        self.reference_label.grid(row=2, column=0, sticky='w')
        self.location_cbox.grid(row=1, column=1, sticky='w')
        self.image_reference_cbox.grid(row=2, column=1, sticky='w')
        self.save_node_button.grid(row=3, column=0, columnspan=2, sticky='w')
        self.loaded_nodes_detail_table.grid(row=4, columnspan=3, column=0, sticky='w')

        # Events
        self.on_set_location = Event()

        # Finalize Init
        self.data_bank.locations.on_store_change += self.set_location_names

        self.data_bank.references.on_store_change += self.set_reference_names
        self.set_location_names()
        self.set_reference_names()

    def select_reference(self, event):
        name = self.image_reference_cbox_var.get()
        logger.debug(f"Getting reference for new node with name {name}")
        self.reference = self.data_bank.references.get_variable_value(name)
        logger.debug(f"Reference found is {self.reference}")
        print(self.reference.name)
        print(self.data_bank.references.get_all())
        if self.test_tracker is not None:
            self.remove_test_tracker()
        self.test_tracker = Tracker(self.reference)
        self.add_test_tracker()

    def select_location(self, event):
        name = self.location_cbox_var.get()
        print(name)
        self.location = self.data_bank.locations.get_variable_value(name)
        print(self.location)
        self.on_set_location(self.location)

    def add_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.add_tracker(self.test_tracker)

    def remove_test_tracker(self):
        if self.test_tracker is not None:
            self.image_scanner.remove_tracker(self.test_tracker)

    def set_reference_names(self, key=None, value=None):
        names = []
        for ref in self.data_bank.references.get_all():
            names.append(ref)
        self.image_reference_cbox['values'] = names

    def set_location_names(self, key=None, value=None):
        names = []
        for loc in self.data_bank.locations.get_all():
            names.append(loc)
        self.location_cbox['values'] = names

    def save_node(self):
        if self.reference is None:
            logger.warning(f"Node not saved. Reference was not found")
            return
        if self.reference.match is None:
            logger.warning(f"Node not saved. Reference match was not found")
            return
        if self.location is None:
            logger.warning(f"Node not saved. Location was not found")
            return
        self.remove_test_tracker()
        self.test_tracker = None
        player_pos = self.data_bank.dynamic_variables.get_variable_value("player position")
        match_pos = self.reference.match.center
        self.node_mapper.create_new_node(player_pos, match_pos, self.reference, self.location)

