import threading
import logging
import cv2

from Client.imaging.management import ImageManager

logger = logging.getLogger(__name__)

from tkinter import ttk
from Client.cli import CustomCLI
from Client.data.bank import DataBank
from Client.imaging.processing import ImageProcessor
from Client.input_handling.switch_relay import SwitchToPiController
from Client.navigation.nodes import NodeNavigator
from Client.tasks.task_processor import TaskProcessor, TaskAssembler


class SwitchBot:
    def __init__(self, game_name):
        self.data_bank = DataBank()
        # self.switch_relay = SwitchToPiController()
        # self.node_navigator = NodeNavigator()
        self.imaging_manager = ImageManager()
        # self.task_assembler = TaskAssembler(game_name)
        # self.task_processor = TaskProcessor(self.task_assembler, self.node_navigator, self.image_processor)

        # Start CLI
        self.cli = CustomCLI()
        # self.register_cli_commands()
        # self.cli.list_commands()
        # self.cli.start_cli()

    def _new_node(self):
        self.node_navigator.create_new_node(self.image_processor.bot_frame.copy())

    def _main_loop(self):
        while True:
            k = cv2.waitKey(1)
            self.imaging_manager.process_images()

    def start_main_loop(self):
        logger.debug("Starting Imaging thread")
        thread = threading.Thread(target=self._main_loop)
        thread.start()
