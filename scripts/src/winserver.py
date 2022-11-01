import atexit
import sys

from publisher import publisher
from subscriber import subscriber

class winserver:
    def __init__(self, whoami, HOST = "127.0.0.1", PORT = 27015):

        ## Default Master URI
        self.__HOST__ = HOST
        self.__PORT__ = PORT

        self.__pubs__ = []
        self.__subs__ = []
        self.__whoami__ = whoami

        self.__ext_dev__ = False
        if HOST != '127.0.0.1':
            self.__ext_dev__ = True
        # atexit.register(self.shutdown())

    ## Register a publisher for advertising
    def advertise(self, topic, msg_type, qlen, __HOST__=None):
        pub = publisher(topic, msg_type, qlen)

        if __HOST__ != None:
            pub.__set_host__(__HOST__)

        pub.__setup__(self.__HOST__, self.__PORT__)
        self.__pubs__.append(pub)
        return pub

    ## Create a subscriber
    def subscribe(self, topic, msg_type, call_back, qlen):
        s = subscriber(topic, msg_type, call_back, qlen)
        s.__setup__(self.__HOST__, self.__PORT__)
        self.__subs__.append(s)

        return s

    def spin(self):
        while True:
            for sub in self.__subs__:
                sub.__check_queue__()

    def spinOnce(self):
        for sub in self.__subs__:
            sub.__check_queue__()

    def shutdown(self):
        for p in self.__pubs__:
            p.shutdown()
        for s in self.__subs__:
            s.shutdown()

## MAIN ##
def signal_handler(sig, frame):
    sys.exit(1)

if __name__ == '__main__':
    pass