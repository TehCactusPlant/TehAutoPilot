import threading
import logging
import cv2
from Client.imaging.management import ImageManager
from Client.data.bank import DataBank
from Client.input_handling.control import SwitchProPiControllerRelay
from Client.input_handling.management import InputManager

logger = logging.getLogger(__name__)


class SwitchBot:
    def __init__(self, game_name):
        self.data_bank = DataBank()
        self.imaging_manager = ImageManager()
        self.switch_relay = SwitchProPiControllerRelay()
        self.input_manager = InputManager(self.switch_relay)
        # self.node_navigator = NodeNavigator()
        # self.task_assembler = TaskAssembler(game_name)
        # self.task_processor = TaskProcessor(self.task_assembler, self.node_navigator, self.image_processor)

    def _main_loop(self):
        while True:
            k = cv2.waitKey(1)
            self.imaging_manager.process_images()

    def start_main_loop(self):
        self.switch_relay.start_bg_thread()
        logger.debug("Starting Imaging thread")
        thread = threading.Thread(target=self._main_loop)
        thread.start()
