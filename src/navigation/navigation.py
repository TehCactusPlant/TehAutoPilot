from src.common_utils.models import Event
from src.models.core import Node
from src.navigation.nodes import NodeMapping


class NodeNavigator:
    def __init__(self):
        self.node_mapping = NodeMapping()
        self.on_node_arrival = Event()

    def a_star_pathfind(self, node1: Node, dest_node: Node, paths: list[list],path: list[Node]):
        path.append(node1)
        for con_node in node1.node_links:
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
