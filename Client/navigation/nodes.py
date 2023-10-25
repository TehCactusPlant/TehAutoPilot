from Client.common_utils.models import Event, ReactiveList
from Client.imaging.scanning import ImageScanner, Tracker
from Client.models.core import *
import Client.common_utils.cv_drawing as drawing_utils
import logging

logger = logging.getLogger(__name__)


class NodeMapping:
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info('Creating new NodeMapping')
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.image_scanner = ImageScanner()
        self.mapping_depth = 3
        self.loaded_nodes = {}
        self.mapped_nodes: ReactiveList[Node] = ReactiveList()
        self.node_links = []
        self.current_node = None
        self.last_node = None
        self.data_bank = DataBank()

        # Events
        self.on_mapping_update = Event()
        self.on_node_change = Event()
        self.on_node_change += self.update_mapped_nodes

    def create_new_node(self, player_pos: Point, ref_position: Point, reference, location):
        x_off = player_pos.x - ref_position.x
        y_off = player_pos.y - ref_position.y
        vect = Vector.from_points(player_pos, ref_position)
        new_node = Node(None, location, x_off, y_off, reference)
        new_node.save()
        if self.current_node is not None:
            logger.debug("Linking nodes during create process.")
            new_link = NodeLink(None, new_node, self.current_node, vect.magnitude, vect.direction)
            new_link.save()
        self.image_scanner.add_tracker(Tracker(new_node.reference))
        self.loaded_nodes[str(new_node.get_id())] = new_node
        self.change_nodes(new_node)

    def change_nodes(self, new_node):
        if self.current_node is not None:
            self.last_node = self.current_node
        self.current_node = new_node
        self.on_node_change(new_node)

    def update_mapped_nodes(self, node): # Triggers when node changes
        self.mapped_nodes.clear()
        self.mapped_nodes.append(node)
        self.get_mappable_nodes(node, 0)

    def get_mappable_nodes(self, node: Node, depth=0):
        depth += 1
        if depth < self.mapping_depth:
            for node_link in node.node_links:
                conn_node = node_link.get_other_node(node)
                self.mapped_nodes.append(conn_node)
                self.get_mappable_nodes(conn_node, depth)

    def draw_mapped_nodes(self, output_image):
        for node in self.mapped_nodes:
            node.position = Point(0, 0)
            node.is_drawn = False
            self.data_bank.update_debug_entry("Nodes mapped", len(self.mapped_nodes))
            ref_loc = None
            if node.reference.match is not None:
                ref_loc = node.reference.match.center
                node.position = Point(ref_loc.x + node.x_off, ref_loc.y + node.y_off)
            match_location = node.position
            is_destination = True if node == self.current_node else False
            is_assumed = False if ref_loc is not None else True
            self.data_bank.update_debug_entry("assumed node", is_assumed)
            self.data_bank.update_debug_entry("is destination", is_destination)
            if is_assumed:
                conn_node = None
                conn_link: NodeLink = None
                for link in node.node_links:
                    temp_node = link.get_other_node(node)
                    if node.is_drawn:
                        conn_node = temp_node
                        break
                if conn_link is not None:
                    vect = conn_link.dir_vector
                    # Get Terminal Point THIS IS A TO DO STILL. MATH THIS GOOD
                    node.position = vect.get_terminal_point(conn_node.position)
            else:
                # Map with match data
                node.is_drawn = True
                drawing_utils.draw_line_from_points(output_image, ref_loc,
                                                    node.position, drawing_utils.
                                                    RGBColors.LIGHT_BLUE)
            drawing_utils.draw_node(output_image, node.position, is_destination, is_assumed)

        player_pos = self.data_bank.dynamic_variables.get_variable_value("player position")
        if self.current_node is not None:
            drawing_utils.draw_line_from_points(output_image, player_pos,
                                                self.current_node.position,
                                                drawing_utils.RGBColors.BLUE)
