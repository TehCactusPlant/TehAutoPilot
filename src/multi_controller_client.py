import socket
from input_handling.input_processor import *
from time import sleep
import threading
import logging
logger = logging.getLogger(__name__)


class SwitchClient:
    HOST = '192.168.0.11'  # The server's hostname or IP address
    PORT = 50001      # The port used by the server
    DELAY = 0.02    # Delay because client can send 100,000+ times faster than server recvs
    MSG_SFX = "[END]"
    display = None
    config = None
    socket = None
    connected = False

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """
    Main loop that compiles Xinputs into a single MultiController object
    """
    def main(self):
        # Create UI Thread thing, needs to be referencable.
        logger.info(f"Connecting to {self.HOST} via port {self.PORT}")
        # Start connection thread
        conn_thread = threading.Thread(target=self.client_server_connection_loop)
        conn_thread.start()
        local_controller = SwitchPacketAssembler()
        while True:
            sleep(self.DELAY) # SHIT GOIN' TO FAST
            # Get State
            new_state = local_controller.assemble_state_manual()
            msg = json.dumps(new_state) + self.MSG_SFX
            # Encode and send if connected
            if self.connected:
                try:
                    msg = str.encode(msg)
                    type(msg)
                    self.socket.sendall(msg)
                except Exception as e:
                    logger.error("Error occured during main loop. Assuming disconnect, setting state to disconnected")
                    self.connected = False

            # Update display

    def start_bg_thread(self):
        global t
        thread = threading.Thread(target=self.main,)
        thread.start()
    
    def start_connection(self):
        try:
            self.socket.connect((self.HOST, self.PORT))
            self.connected = True
            logger.info("Connected to server successfully.")
        except Exception as e:
            logger.error("Failed to connect to server. full error:")
            logger.error(e)

    def client_server_connection_loop(self):
        while True:
            if not self.connected:
                logger.info("Not connected to server, attempting connection")
                self.start_connection()
            sleep(10)


if __name__ == "__main__":
    t = SwitchClient()
    t.start_bg_thread()
    while True:
        pass
    