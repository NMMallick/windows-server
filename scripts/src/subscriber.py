import atexit
from copy import deepcopy
import socket
import select
import threading


__CLOSE_CONN__ = bytes('\x03', 'utf-8')
__SUB__ = bytes('\x01', 'utf-8')

class subscriber:
    def __init__(self, topic, msg_type, callback, qlen):
        atexit.register(self.shutdown)

        self.__callback__ = callback
        self.__msg__ = msg_type()
        self.__topic__ = topic
        self.__msg_queue__ = []
        self.__qlen__ = qlen

        ## Thread control variables
        self.__qlock__ = threading.Lock()
        self.__done__ = False
        self.__isConnected__ = False

        # self.__pthread__ = None
        self.__mthread__ = None
        self.__threads__ = []

        self.__ext_dev__ = False

        ## No active publisher identity
        self.__PUB_URI__ = ('0.0.0.0', 0x0000)


    def shutdown(self):
        print('Shutting down subscriber')
        self.__done__ = True

        for thr in self.__threads__:
            thr.join()

    def __setup__(self, HOST, PORT):

        ## Thread for listen to the main
        #   server
        self.__stop_pthread__ = False
        self.__mthread__ = threading.Thread(target=self.__supervisor__, args=(HOST, PORT,), daemon=True)

        self.__mthread__.start()

    def __supervisor__(self, HOST, PORT):

        if HOST != '127.0.0.1':
            self.__ext_dev__ = True

        ## Connect to master and wait for info on a publisher.
        #   we depend on the master to be ALWAYS running,
        #   so if it shuts down, so do we
        __pthread__ = threading.Thread(target=self.__publisher_conn__, daemon=True)
        self.__threads__.append(__pthread__)

        __master_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __master_sock__.connect((HOST, PORT))

        __msg__ = self.__serialize_request__(self.__topic__)
        __master_sock__.send(__msg__)

        __res__ = __master_sock__.recv(512)
        self.__PUB_URI__ = self.__get_addr__(__res__)
        print(self.__PUB_URI__)

        ## port number of 0 means no active
        #   publisher within this context
        if self.__PUB_URI__[1] != 0:
            __pthread__.start()

        ## Setting the master socket to non-blocking
        __master_sock__.setblocking(False)
        while not self.__done__:

            readable, writable, exceptional = select.select([__master_sock__], [], [__master_sock__], 0.001)

            for s in exceptional:
                print('Err: main server has shut down')
                s.close()
                self.shutdown()

            for s in readable:
                __data__ = __master_sock__.recv(512)

                if not __data__:
                    print("Err: master socket closed the connection")
                    self.shutdown()

                self.__PUB_URI__ = self.__get_addr__(__data__)

                if self.__PUB_URI__[1] != 0:
                    ## End the current publisher connections
                    if __pthread__.is_alive():
                        self.__stop_pthread__ = True
                        __pthread__.join()

                    print("connecting to pub")

                    ## Reconnect to the new pub addr
                    __pthread__ = threading.Thread(target=self.__publisher_conn__, daemon=True)
                    __pthread__.start()
                else:
                    ## Reclaim resources from the worker thread
                    #   since there is no active publisher on that
                    #   given topic
                    self.__stop_pthread__ = True
                    __pthread__.join()

        ## Set setinel variable to stop
        #   the pub connection
        self.__stop_pthread__ = True

        ## Join the pub connection worker
        #   thread
        __pthread__.join()
        __master_sock__.close()

    def __publisher_conn__(self):

        ## This connection will be set to
        #   non-blocking since its the only
        #   connection we need to listen to
        __pub_conn__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"attempting to connect to {self.__PUB_URI__[0]}, {self.__PUB_URI__[1]} ...")

        try:
            __pub_conn__.connect(self.__PUB_URI__)
        except Exception as e:
            print("Err: could not connect to publisher")
            print(e)
            return

        __pub_conn__.setblocking(False)

        ## Check for messages or disconnects from
        #   the publisher.
        while not self.__done__ and not self.__stop_pthread__:
            ## Wait for a message - times out
            #   every millisecond so we can check for
            #   the done condition
            readable, writable, exceptional = select.select([__pub_conn__], [], [__pub_conn__])

            ## Checking connection status
            for s in exceptional:
                print("Err:  closed connection")
                s.close()
                return

            ## Checking for new data coming in
            for s in readable:
                __msg__ = s.recv(4096)

                if not __msg__:
                    print("connection closed")
                    s.close()
                    return

                with self.__qlock__:
                    if len(self.__msg_queue__) < self.__qlen__:
                        self.__msg_queue__.append(deepcopy(__msg__))
                    else:
                        self.__msg_queue__.pop(0)
                        self.__msg_queue__.append(deepcopy(__msg__))

    def __check_queue__(self):
        with self.__qlock__:
            ## No messsages
            if len(self.__msg_queue__) == 0:
                return

            ## Service the front of the queue
            __buffered_data__ = self.__msg_queue__.pop(0)
            self.__msg__.deserialize(__buffered_data__)

            ## Send the message through the callback
            self.__callback__(self.__msg__)


    def __get_addr__(self, res):

        if len(res) != 6:
            return

        ## Extract the host name and port address
        if self.__ext_dev__:
            host = str(res[0]) + '.' + str(res[1]) + '.' + str(res[2]) + '.' + str(res[3])
        else:
            print('else is being called')
            host = '127.0.0.1'
        port = (res[4] << 8) | res[5]

        return (host, port)

    def __serialize_request__(self, topic):

        msg = bytearray(__SUB__)
        topic_len = len(topic)
        msg += topic_len.to_bytes(1, 'big')
        msg += topic.encode('utf-8')

        return msg

## Test callback
def test(msg):
    print(msg.my_str)

if __name__ == '__main__':

    # s = subscriber('/scan', wayside, test, 1)
    # s.__setup__('127.0.0.1', 27015)

    # while True:
    #     s.__check_queue__()
    pass


