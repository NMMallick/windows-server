import sys
import socket
import struct


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 27015))
    
    data = bytes('\x03', 'utf-8')
    print(data)
    s.send(struct.pack('c', data))

    # data = s.recv(4096)
    
    print(s.shutdown(socket.SHUT_RDWR))
    s.close()