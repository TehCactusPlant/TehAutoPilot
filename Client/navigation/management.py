from Client.models.management import Manager
import logging

from Client.navigation.navigation import NodeNavigator
from Client.navigation.nodes import NodeMapping

logger = logging.getLogger(__name__)

class NavigationManager(Manager):
    def __init__(self):
        super().__init__()

        self.node_mapper = NodeMapping()
        self.node_navigator = NodeNavigator()
