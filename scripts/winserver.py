import signal
import sys
import publisher

from time import sleep
from tests.wayside_controller import wayside

class winserver:
    def __init__(self, HOST = "127.0.0.1", PORT = 27015):

        ## Default Master URI
        self.__PORT__ = PORT
        self.__HOST__ = HOST

    ## Register a publisher for advertising
    def advertise(self, topic, msg_type, buff_size):
        pub = publisher(topic, msg_type, buff_size)
        pub.__setup__(self.__HOST__, self.__PORT__)

        return pub

## MAIN ##
def signal_handler(sig, frame):
    sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    msg = wayside()
    msg.my_bools = [True, True, True]
    msg.my_int = 10
    msg.my_str = "hello"

    r = winserver()
    p = r.advertise('/scan', wayside, 1)
    q = r.advertise('/odom', wayside, 1)

    while True:
        p.publish(msg)
        sleep(2.0)

    # sleep(5.0)

        # print("Shutting down subscriber")
        # p.shutdown()