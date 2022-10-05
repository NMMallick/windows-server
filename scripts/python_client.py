from cmath import inf
import socket
import time
import sys

PORT = 27015
HOST = "127.0.0.1"

message = "hello"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(((HOST, PORT)))
    time.sleep(2.0);

    print(f"Sending {sys.getsizeof(message.encode('utf-8'))} bytes")
    s.send(message.encode('utf-8'))


    while True:
        continue
