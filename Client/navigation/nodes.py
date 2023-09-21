import Client.cact_utils.data_utils as data_utils
from Client.database.core import DBInterface
from Client.models.core import *


class NodeNavigator:
    def __init__(self):
        self.db = DBInterface()
        self.nodes = {}
        self.locations: list[Location] = self.db.get_locations()
        self.current_location: Location = self.locations[0]
        self.nodes = self.db.assemble_nodes_by_location(self.current_location)

    def set_location(self, location):
        self.current_location = location

    def get_nodes(self, location: Location):
        # Get Nodes by location - Needs locations assembled from db interface
        nodes = {}
        for i in range(len(nodes)):
            self.nodes[str(i)] = nodes[i]

    def link_nodes(self, node1, node2):
        pass

    def a_star_pathfind(self, node1: Node, dest_node: Node, paths: list[list],path: list[Node]):
        path.append(node1)
        for con_node in node1.connected_nodes:
            if con_node is dest_node:
                # Destination reached: Return
                path.append(dest_node)
                paths.append(path)
                return paths
            elif con_node in path:
                # Bad path break.
                return paths
            else:
                paths = self.a_star_pathfind(con_node, dest_node, paths, path)
        return self.extract_shortest_path(paths)

    def extract_shortest_path(self, paths):
        shortest = []
        for path in paths:
            if len(shortest) <= 0:
                shortest = path
            elif len(path) < len(shortest):
                shortest = path

    def map_nodes(self, node_links: list[NodeLink], nodes: list[Node]):
        for link in node_links:
            node1: Node = self.get_node_by_id(link.node_id1)
            node2: Node = self.get_node_by_id(link.node_id2)
            node1.link(node2)
            node2.link(node1)

    def get_node_by_id(self, node_id):
        return self.nodes[str(node_id)]

    def plot_node(self, node: Node):
        x, y = node.get_detected_position()
        node.position = (x + node.x_off, y + node.y_off)

    def create_new_node(self, base_img):
        data_utils.create_new_node(base_img, self.current_location)
