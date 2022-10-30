import socket
from time import sleep
from wayside_controller import wayside


def serializeRequest(topic):
    msg = bytearray()
    sub_code = 0x01

    msg += sub_code.to_bytes(1, 'big')
    topic_len = len(topic)

    msg += topic_len.to_bytes(1, 'big')
    msg += topic.encode('utf-8')
    return msg

def getAddr(res):

    ## Extract the host name and port address
    host = str(res[0]) + '.' + str(res[1]) + '.' + str(res[2]) + '.' + str(res[3])
    port = (res[4] << 8) | res[5]

    return (host, port)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 27015))

    s.send(serializeRequest('/odom'))

    data = s.recv(4096)
    addr = getAddr(data)

    print(addr[0])
    print(addr[1])

    sleep(5.0)
    s.close()

