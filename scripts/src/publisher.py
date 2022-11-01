import socket
import threading
import select
import atexit
import struct

__CLOSE_CONN__ = bytes('\x03', 'utf-8')
__PUB__ = bytes('\x00', 'utf-8')

class publisher:
    def __init__(self, topic, msg_type, qlen):
        atexit.register(self.shutdown)

        self.message_type = msg_type
        self.topic = topic

        self.__qlen__ = qlen
        self.__pub_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__pub_sock__.bind(('0.0.0.0', 0))
        self.__pub_sock__.listen()

        self.__MY_URI__ = {
            'HOST': self.__pub_sock__.getsockname()[0],
            'PORT': self.__pub_sock__.getsockname()[1]
            }

        print(f"publishing on address {self.__MY_URI__['HOST']}, {self.__MY_URI__['PORT']}")

        ## Connections and threading
        self.__done__ = False
        self.__connections__ = []
        self.__connection_lock__ = threading.Lock

        self.__inputs__ = [ self.__pub_sock__ ]
        self.__outputs__ = []
        self.__clients__ = {}
        self.__master_sock__ = None

    def __set_host__(self, HOST):
        self.__MY_URI__['HOST'] = HOST

    def __setup__(self, HOST, PORT):

        msg = bytearray(__PUB__)

        ## Add HOST addr to the message
        for ip_field in self.__MY_URI__['HOST'].split('.'):
            msg.extend(int(ip_field).to_bytes(1, 'big'))


        ## Add PORT addr to the message
        msg.extend(self.__MY_URI__['PORT'].to_bytes(2, 'big'))
        msg.extend(len(self.topic).to_bytes(1, 'big'))
        msg.extend(struct.pack(f'{len(self.topic)}s', self.topic.encode('utf-8')))

        ## Create socket to master server
        self.__master_sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.__master_sock__.connect((HOST, PORT))
        except:
            print("Err connecting to master! Make sure it's running")
            exit(-1)

        ## Listen for connections in a different thread
        self.__thr__ = threading.Thread(target=self.__connection_loop__, args=(self.__connection_lock__,), daemon=True)
        self.__thr__.start()

        ## Send registration data to the server
        result = self.__master_sock__.send(msg)

        if not result:
            print(f"Err: cannot publish to master server {self.topic}")

    def __connection_loop__(self, lock):

        ## Continuously check for new connections
        ##  until we shut down
        while not self.__done__:

            ## Waiting for an event
            readable, writable, exceptional = select.select(self.__inputs__, self.__outputs__, self.__outputs__, 0.001)

            for s in exceptional:
                with self.__clients__[s]['lock']:
                    self.__inputs__.remove(s)
                    if s in self.__outputs__:
                        self.__outputs__.remove(s)
                    s.close()
                    self.__clients__.pop(s)

            for s in readable:
                if s is self.__pub_sock__:
                    connection, client_address = s.accept()
                    print("client connected")
                    connection.setblocking(0)
                    self.__outputs__.append(connection)
                    self.__clients__[connection] = {"queue" : [], "lock": threading.Lock(),"addr" : client_address}
                else:
                    data = s.recv(4096)
                    if data:
                        msg = struct.unpack('>i', data)
                        if not msg:
                            print("Err: shutdown by master")
                            self.shutdown()

            for s in writable:
                with self.__clients__[s]['lock']:
                    if len(self.__clients__[s]['queue']) > 0:
                        msg = self.__clients__[s]['queue'].pop(0)
                        try:
                            s.send(msg)
                        except:
                            print("Lost connection to client")

                            if s in self.__inputs__:
                                self.__inputs__.remove(s)
                            if s in self.__outputs__:
                                self.__outputs__.remove(s)

                            s.close()
                            self.__clients__.pop(s)


    def publish(self, msg):
        __serial_msg__ = msg.serialize()

        for i in self.__clients__:
            with self.__clients__[i]['lock']:
                if len(self.__clients__[i]['queue']) < self.__qlen__:
                    self.__clients__[i]['queue'].append(__serial_msg__)
                else:
                    self.__clients__[i]['queue'].pop(0) ## pop the front
                    self.__clients__[i]['queue'].append(__serial_msg__)

    def shutdown(self):
        print('shutting down')
        self.__done__ = True

        ## Wait for thread to finish up
        self.__thr__.join()

        ## delete queues
        for i in self.__clients__:
            del self.__clients__[i]['queue']

        ## shutdown subscribed sockets
        for s in self.__outputs__:
            print("closing socket")
            s.shutdown(socket.SHUT_RDWR)
            s.close()


        ## Shut down connection to the master server
        self.__master_sock__.close()

        ## Shut down our own socket connection
        self.__pub_sock__.close()

