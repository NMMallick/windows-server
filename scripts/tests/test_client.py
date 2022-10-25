import sys
import socket
import struct
from time import sleep
from wayside_controller import wayside

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 54431))

    # data = bytes('\x03', 'utf-8')
    # print(data)
    # s.send(struct.pack('c', data))
    msg = wayside()
    data = s.recv(4096)
    msg.deserialize(data)
    print(msg.my_str)

    sleep(5.0)
    s.close()