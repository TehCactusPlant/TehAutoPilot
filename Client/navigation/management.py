from Client.data.bank import DataBank
from Client.imaging.processing import ImageProcessor
from Client.models.management import Manager
import logging

from Client.navigation.navigation import NodeNavigator
from Client.navigation.nodes import NodeMapping

logger = logging.getLogger(__name__)


class NavigationManager(Manager):
    def __init__(self):
        super().__init__()

        self.node_mapper = NodeMapping()
        self.data_bank = DataBank()
        # self.node_navigator = NodeNavigator()

    def process_nodes(self, output_image):

        # Draw Nodes
        self.node_mapper.draw_mapped_nodes(output_image)