from Client.common_utils.models import Event
from Client.models.core import *
import Client.common_utils.cv_drawing as drawing_utils
import logging

logger = logging.getLogger(__name__)


class NodeMapping:
    def __init__(self):
        self.loaded_nodes = {}
        self.mapped_nodes = {}
        self.current_node = None

        # Events
        self.on_mapping_update = Event()

    def link_nodes(self, node1, node2):
        pass

    def draw_nodes(self, output_image):
        pass

    def load_nodes(self):
        pass

    def plot_node(self, node: Node):
        pass

    def create_new_node(self, base_img):
        pass

    def update_mapped_nodes(self):
        pass
