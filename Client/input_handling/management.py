from Client.input_handling.control import Controller
from Client.models.management import Manager
import logging

logger = logging.getLogger(__name__)


class InputManager(Manager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info('Creating new ImageProcessor')
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, controller: Controller=None):
        if self.initialized:
            return
        self.initialized = True
        super().__init__()
        self.controller = controller

