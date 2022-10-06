import socket
import time
import sys

PORT = 27015
HOST = "127.0.0.1"

my_byte = 0x40
message = "hello"


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(((HOST, PORT)))
    
    while True:
        time.sleep(0.001)
        # print(f"Sending {sys.getsizeof(message.encode('utf-8'))} bytes")
        # s.send(message.encode('utf-8'))
        
        # print(f"Sending {sys.getsizeof(message.to_bytes(1, 'little'))} bytes")

        s.send(message.encode('utf-8') + my_byte.to_bytes(1, 'little'))


