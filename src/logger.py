import json
import logging
import socket

class TCPSocketHandler(logging.Handler):
    def __init__(self, host, port, channel):
        super().__init__()
        self.host = host
        self.port = port
        self.channel = channel

    def emit(self, record):
        try:
            message = self.format(record)
            self.send(message)
        except Exception:
            self.handleError(record)

    def send(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            message_json = {'channel':self.channel, 'msg':msg}
            message = json.dumps(message_json)
            s.sendall(message.encode('utf-8'))

# logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/var/log/kaouka.log')
stdout_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
file_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
# Configuration
# tcp_handler = TCPSocketHandler('127.0.0.1', 8001, 1138985405891485849)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# tcp_handler.setFormatter(formatter)
# logger.addHandler(tcp_handler)