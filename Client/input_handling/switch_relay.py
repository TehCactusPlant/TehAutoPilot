import json
import socket
import threading
from time import sleep
import numpy as np
from Client.input_handling.input_processor import SwitchPacketAssembler
import logging
logger = logging.getLogger(__name__)


class ControllerStates:
    Automated = 0,
    Manual = 1


class SwitchToPiController:
    HOST = '192.168.0.11'  # The server's hostname or IP address
    PORT = 50001      # The port used by the server
    DELAY = np.floor(1 / 150)    # Delay because client can send 100,000+ times faster than server recvs
    MSG_SFX = "[END]"
    socket = None
    connected = False
    local_controller = None
    current_c_state = ControllerStates.Manual

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
        self.local_controller = SwitchPacketAssembler()
        while True:
            sleep(self.DELAY)  # SHIT GOIN' TO FAST
            self.process_packet()

    def process_packet(self):
        if self.connected:
            new_state = self.local_controller.current_packet
            if self.current_c_state == ControllerStates.Manual:
                new_state = self.local_controller.assemble_state_manual()
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
        global t
        thread = threading.Thread(target=self.main, )
        thread.start()

    def start_connection(self):
        try:
            self.socket.connect((self.HOST, self.PORT))
            self.connected = True
            logger.info("Connected to server successfully.")
        except Exception as e:
            logger.error("Failed to connect to server. full error:")
            logger.error(e)