import json
import socket
import threading
from time import sleep
import numpy as np

from Client.common_utils.models import Event
from Client.input_handling.input_processor import SwitchPacketAssembler
import logging

logger = logging.getLogger(__name__)


class ControllerStates:
    Automated = 0
    Manual = 1


class Controller:
    current_c_state = ControllerStates.Manual

    def __init__(self):
        self.on_state_change = Event()
        self.thread = None

    def set_automation_state(self, is_manual: bool):
        logger.debug(f"Manual Controller control toggled to {is_manual}")
        if is_manual:
            self.current_c_state = ControllerStates.Manual
        else:
            self.current_c_state = ControllerStates.Automated
        self.on_state_change()


class SwitchProPiControllerRelay(Controller):
    HOST = '192.168.86.49'  # The server's hostname or IP address
    PORT = 50001  # The port used by the server
    DELAY = 1 / 150  # Delay because client can send 100,000+ times faster than server recvs
    MSG_SFX = "[END]"
    socket = None
    connected = False
    local_controller = None

    def client_server_connection_loop(self):
        while True:
            if not self.connected:
                logger.error("Not connected to server, attempting connection")
                self.start_connection()
            sleep(10)

    def main(self):
        # Create UI Thread thing, needs to be referencable.
        logger.info(f"Connecting to {self.HOST} via port {self.PORT}")
        # Start connection thread
        conn_thread = threading.Thread(target=self.client_server_connection_loop)
        conn_thread.start()
        self.local_controller = SwitchPacketAssembler(self.DELAY)
        while True:
            sleep(self.DELAY)
            self.process_packet()

    def process_packet(self):
        if self.connected:
            new_state = self.local_controller.current_packet
            if self.current_c_state == ControllerStates.Manual:
                new_state = self.local_controller.assemble_state_keyboard()
            elif self.current_c_state == ControllerStates.Automated:
                new_state = self.local_controller.assemble_state_automated()
            msg = json.dumps(new_state) + self.MSG_SFX
            try:
                msg = str.encode(msg)
                type(msg)
                self.socket.sendall(msg)
            except Exception as e:
                logger.error("Error occured during main loop. Assuming disconnect, setting state to disconnected")
                self.connected = False

    def start_bg_thread(self):
        self.thread = threading.Thread(target=self.main, )
        self.thread.start()

    def start_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            logger.info("Attempting to connect to server...")
            self.socket.connect((self.HOST, self.PORT))
            self.connected = True
            logger.info("Connected to server successfully.")
        except Exception as e:
            logger.error("Failed to connect to server. full error:")
            logger.error(e)
