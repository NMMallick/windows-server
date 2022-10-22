import socket
import time
import sys

my_byte = 0x40
message = "hello"


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect(((HOST, PORT)))

#     while True:
#         time.sleep(0.001)
#         # print(f"Sending {sys.getsizeof(message.encode('utf-8'))} bytes")
#         # s.send(message.encode('utf-8'))

#         # print(f"Sending {sys.getsizeof(message.to_bytes(1, 'little'))} bytes")

#         s.send(message.encode('utf-8') + my_byte.to_bytes(1, 'little'))

class publisher:
    def __init__(self, topic, msg_type, buff_size):
        self.message_type = msg_type
        self.topic = topic
        self.__bufflen__ = buff_size

        self.__pub_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__pub_sock__.bind(('127.0.0.1', 0))

        self.__MY_URI__ = {
            'HOST': self.__pub_sock__.getsockname()[0],
            'PORT': self.__pub_sock__.getsockname()[1]
            }

        print(self.__MY_URI__)

    def __setup__(self, HOST, PORT):

        msg = bytearray(b'\00')

        ## Add HOST addr to the message
        for ip_field in self.__MY_URI__['HOST'].split('.'):
            msg.extend(int(ip_field).to_bytes(1, 'big'))

        ## Add PORT addr to the message
        msg.extend(self.__MY_URI__['PORT'].to_bytes(2, 'big'))
        print(msg)

        self.__master_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__master_sock__.connect((HOST, PORT))
        except:
            print("Err connecting to master! Make sure it's running")
            exit(-1)

        ## Send registration data to the server w
        self.__master_sock__.sendall(msg)

        # time.sleep(5.0)

    def publish(self, msg):
        pass

    def shutdown(self):
        pass

class winserver:
    def __init__(self, HOST = "127.0.0.1", PORT = 27015):
        ## Default Master URI
        self.__PORT__ = PORT
        self.__HOST__ = HOST

    def whoami(self, me):
        pass

    ## Register a publisher for advertising
    def advertise(self, topic, msg_type, buff_size):
        pub = publisher(topic, msg_type, buff_size)
        pub.__setup__(self.__HOST__, self.__PORT__)
        return pub


if __name__ == '__main__':

    r = winserver()
    r.advertise('/scan', int, 1)