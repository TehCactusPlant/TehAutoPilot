#State Relay connects PC to Raspberry-Pi(or any client) to quickly relay
#json objects from clients to server objects.
import socket

class StateRelayClient:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def SendToServer(self, msg):
        self.sock.sendall(msg)

    async def ReceiveFromServer(self, size):
        return self.sock.recv(size)
