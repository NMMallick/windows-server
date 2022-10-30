import socket
import select
import threading

from yaml import serialize

__CLOSE_CONN__ = bytes('\x03', 'utf-8')
__SUB__ = bytes('\x01', 'utf-8')

class subscriber:
    def __init__(self, topic):

        self.__qlock__ = threading.Lock

        self.__topic__ = topic
        self.__done__ = False
        self.__pub_conn_status__ = False


    def __setup__(self, HOST, PORT):

        ## Connect to master and wait
        #   for info on a publisher
        self.__master_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__master_sock__.connect((HOST, PORT))

        __msg__ = self.__serializeRequest__(self.__topic__)
        self.__master_sock__.send(__msg__)

        __res__ = self.__master_sock__.recv(512)
        self.__PUB_URI__ = self.__getAddr__(__res__)


        # self.__master_thr__ = threading.Thread(target=self.__master_conn__, args=(HOST, PORT,), daemon=True)

        return

    def __supervisor__(self, HOST, PORT):

        while not self.__done__:

            readable, writable, exceptional = select.select(self.__inputs__, self.__outputs__, self.__outputs__)


        return

    def __publisher_conn__(self, HOST, PORT):
        __pub_conn__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    def __getAddr__(self, res):

        ## Extract the host name and port address
        host = str(res[0]) + '.' + str(res[1]) + '.' + str(res[2]) + '.' + str(res[3])
        port = (res[4] << 8) | res[5]

        return (host, port)

    def __serializeRequest__(topic):
        msg = bytearray(__SUB__)

        topic_len = len(topic)

        msg += topic_len.to_bytes(1, 'big')
        msg += topic.encode('utf-8')

        return msg
