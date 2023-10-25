import threading
import logging
import cv2

from Client.common_utils.models import Point
from Client.imaging.management import ImageManager
from Client.data.bank import DataBank
from Client.input_handling.control import SwitchProPiControllerRelay
from Client.input_handling.management import InputManager
from Client.navigation.management import NavigationManager

logger = logging.getLogger(__name__)


class SwitchBot:
    def __init__(self, game_name):
        self.data_bank = DataBank()
        self.imaging_manager = ImageManager()
        self.switch_relay = SwitchProPiControllerRelay()
        self.input_manager = InputManager(self.switch_relay)
        self.navigation_manager = NavigationManager()
        # self.task_assembler = TaskAssembler(game_name)
        # self.task_processor = TaskProcessor(self.task_assembler, self.node_navigator, self.image_processor)
        self.base_init = self.default_base_init

    def default_base_init(self):
        self.data_bank.dynamic_variables.thread_safe_update_variable("player position", Point(480, 270))
        self.data_bank.dynamic_variables.thread_safe_update()

    def _main_loop(self):
        """
        1. Process Images
        2. Process Nodes
        3. Process Steps/Tasks
        4. Process Logic for next iteration - Dynamic Variables
        5. Thread safe updates that are not done before
        """
        while True:
            k = cv2.waitKey(1)
            # 1
            self.imaging_manager.process_images()
            im_out = self.imaging_manager.im_processor.frames['main output'].get_main_image()
            # 2
            self.navigation_manager.process_nodes(im_out)
            # 3
            # 4
            # 5
            self.data_bank.dynamic_variables.thread_safe_update()
            self.imaging_manager.im_processor.finalize_output()

    def start_main_loop(self):
        self.switch_relay.start_bg_thread()
        logger.debug("Starting Imaging thread")
        self.base_init()
        thread = threading.Thread(target=self._main_loop)
        thread.start()
